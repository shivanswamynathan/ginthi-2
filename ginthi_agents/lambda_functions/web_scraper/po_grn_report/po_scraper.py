import argparse
import os
import time
from datetime import datetime
from pathlib import Path

import boto3
import pandas as pd
from dotenv import load_dotenv
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


# ---------- Core scraper (reusable) ----------
def scrape_purchase_order_data(
    email,
    password,
    headless=True,
    base_url="https://supplynote.in",
    upload_to_s3=True,
    s3_bucket=None,
    is_lambda=False,
):
    """
    Core Playwright logic for purchase order data scraping.
    Reusable by both Lambda and local entrypoints.
    """
    # Determine launch args based on environment
    if is_lambda or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--no-zygote",
            "--single-process",
            "--disable-gpu",
            "--disable-gpu-sandbox",
            "--disable-gpu-compositing",
            "--disable-accelerated-2d-canvas",
            "--disable-accelerated-video-decode",
            "--disable-dev-shm-usage",
            "--disable-software-rasterizer",
            "--use-gl=swiftshader",
            "--use-angle=swiftshader",
            "--disable-web-security",
            "--ignore-certificate-errors",
            "--window-size=1280,800",
            "--hide-scrollbars",
            "--mute-audio",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-client-side-phishing-detection",
            "--renderer-process-limit=1",
            "--no-startup-window",
            "--no-first-run",
            "--disable-default-apps",
            "--no-service-autorun",
            "--password-store=basic",
        ]
    else:
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ]

    with sync_playwright() as p:
        print(f"🧠 Launching Chromium (headless={headless}) for PO scraping...")
        browser = None
        local_file_path = None

        try:
            print(f"🔧 Launch args: {len(launch_args)} arguments configured")
            browser = p.chromium.launch(
                headless=headless,
                args=launch_args,
                timeout=120000,
                slow_mo=100 if not headless else 0,
            )
            
            context = browser.new_context(
                accept_downloads=True,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            page.set_default_timeout(60000)
            print("✅ Browser launched successfully")

            # Step 1: Login
            login_url = f"{base_url}/signin"
            page.goto(login_url, timeout=60000)
            print("🌐 Navigated to login page.")

            page.fill("input[name='username']", email)
            page.fill("input[id='id_password']", password)
            page.click("button[type='submit']")

            page.wait_for_url("**/dashboard", timeout=60000)
            print("✅ Login successful! Current URL:", page.url)

            # Step 2: Navigate to Reports
            print("📊 Step 1: Clicking Reports button in sidebar...")
            page.wait_for_selector("text=Reports", timeout=30000)
            page.click("text=Reports", force=True)
            print("✅ Reports button clicked")
            time.sleep(3)

            # Step 3: Click PO-GRN Docs Report
            print("📋 Step 2: Clicking 'PO-GRN Docs Report' card...")
            page.wait_for_selector("text=PO-GRN Docs Report", timeout=60000)
            page.click("text=PO-GRN Docs Report", force=True)
            print("✅ 'PO-GRN Docs Report' card clicked")
            time.sleep(10)

            # Step 4: Date range (keeping default)
            print("📅 Checking date range...")
            time.sleep(1)
            print("✅ Date range kept as default")

            # Step 5: Select vendors (optional - selecting first 3)
            print("🔍 Selecting vendor filters...")
            time.sleep(1)
            
            try:
                multiselect = page.query_selector('p-multiselect[formcontrolname="vendors"]')
                if multiselect:
                    multiselect.click(force=True)
                    time.sleep(2)

                    checkboxes = page.query_selector_all(
                        'p-multiselect[formcontrolname="vendors"] .p-checkbox'
                    )
                    print(f"📌 Found {len(checkboxes)} vendor checkboxes")

                    count = 0
                    for checkbox in checkboxes:
                        if count >= 3:
                            break
                        checkbox.click(force=True)
                        count += 1
                        time.sleep(0.5)
                        print(f"✅ Selected vendor {count}")

                    page.click("body", force=True)
                    print(f"✅ {count} vendors selected")
                else:
                    print("⚠️ Vendor dropdown not found, skipping")
            except Exception as e:
                print(f"⚠️ Vendor selection failed: {e}")

            # Step 6: Generate Report
            print("🚀 Looking for 'Show Report' button...")
            page.wait_for_selector('button:has-text("Show Report")', timeout=15000)
            
            print("▶️ Clicking 'Show Report' button...")
            page.click(
                'button.md-raised.md-primary.low-shadow-card:has-text("Show Report")',
                force=True,
            )
            
            print("⏳ Waiting for report generation...")
            time.sleep(10)
            print("✅ Purchase Order report generated successfully")

            # Step 7: Download Report
            print("📥 Downloading Purchase Order report...")
            page.wait_for_selector('button:has-text("Export CSV")', timeout=30000)
            print("✅ Found 'Export CSV' button")

            export_button = page.query_selector('button:has-text("Export CSV")')
            
            if not export_button:
                raise RuntimeError("❌ 'Export CSV' button not found")

            with page.expect_download() as download_info:
                export_button.click(force=True)
                print("✅ Export button clicked")

            download = download_info.value
            time.sleep(3)

            # Step 8: Save file with timestamp
            current_datetime = datetime.now()
            temp_dir = Path("/tmp") if os.path.exists("/tmp") else Path(".")
            temp_file = temp_dir / f"purchase_order_report_temp_{current_datetime.strftime('%Y%m%d_%H%M%S')}.xlsx"

            download.save_as(str(temp_file))
            print(f"✅ Purchase Order report downloaded: {temp_file}")

            # Step 9: Add data_version column
            df = pd.read_excel(temp_file)
            df["data_version"] = current_datetime
            df.to_excel(temp_file, index=False, engine='openpyxl')
            print("✅ Added 'data_version' column to report")

            local_file_path = str(temp_file)

            # Step 10: Upload to S3 if enabled
            if upload_to_s3 and s3_bucket:
                s3_path = upload_to_s3_bucket(
                    local_file_path, s3_bucket, current_datetime
                )
                print(f"☁️ File uploaded to S3: {s3_path}")
                result = {
                    "ok": True,
                    "message": "Purchase Order data scraped and uploaded to S3.",
                    "local_path": local_file_path,
                    "s3_path": s3_path,
                }
            else:
                result = {
                    "ok": True,
                    "message": "Purchase Order data scraped successfully (local only).",
                    "local_path": local_file_path,
                }

            return result

        except PlaywrightTimeoutError as e:
            print(f"⚠️ Timeout occurred: {e}")
            raise
        except Exception as e:
            print(f"💥 Scraping failed: {e}")
            try:
                page.screenshot(path="po_scraping_error.png")
                print("📸 Error screenshot saved: po_scraping_error.png")
            except:
                pass
            raise
        finally:
            if browser:
                try:
                    browser.close()
                    print("🧹 Browser closed successfully.")
                except Exception as e:
                    print(f"⚠️ Error closing browser: {e}")


# ---------- S3 Upload Function ----------
def upload_to_s3_bucket(local_file_path, s3_bucket, upload_datetime):
    """
    Upload the Excel file to S3 with date-based folder structure:
    s3://bucket/supply_note/purchase_order_data/YYYY/MM/DD/purchase_order_report_YYYYMMDD_HHMMSS.xlsx
    """
    try:
        # Parse bucket name - extract just the bucket name
        s3_input = s3_bucket.replace("s3://", "").strip("/")
        bucket_name = s3_input.split("/")[0]
        
        # Create S3 path with date structure
        year = upload_datetime.strftime("%Y")
        month = upload_datetime.strftime("%m")
        day = upload_datetime.strftime("%d")
        filename = f"purchase_order_report_{upload_datetime.strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Path: supply_note/purchase_order_data/YYYY/MM/DD/
        s3_key = f"supply_note/purchase_order_data/{year}/{month}/{day}/{filename}"

        print(f"📤 Uploading to S3: s3://{bucket_name}/{s3_key}")

        # Initialize S3 client with credentials from environment
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY"),
            region_name=os.getenv("S3_BUCKET_REGION", "ap-south-1")
        )

        # Upload file
        s3_client.upload_file(local_file_path, bucket_name, s3_key)

        full_s3_path = f"s3://{bucket_name}/{s3_key}"
        print(f"✅ Successfully uploaded to: {full_s3_path}")

        return full_s3_path

    except Exception as e:
        print(f"❌ S3 upload failed: {e}")
        raise

# ---------- Lambda entrypoint ----------
def handler(event=None, context=None):
    """
    AWS Lambda handler.
    Expects environment variables:
    - SUPPLYNOTE_EMAIL
    - SUPPLYNOTE_PASSWORD
    - S3_BUCKET
    """
    print("🚀 Starting Purchase Order scraping (Lambda)...")

    if event:
        email = event.get("email") or os.getenv("SUPPLYNOTE_EMAIL", "")
        password = event.get("password") or os.getenv("SUPPLYNOTE_PASSWORD", "")
        s3_bucket = event.get("s3_bucket") or os.getenv("S3_BUCKET", "")
        headless = event.get("headless", True)
    else:
        email = os.getenv("SUPPLYNOTE_EMAIL", "")
        password = os.getenv("SUPPLYNOTE_PASSWORD", "")
        s3_bucket = os.getenv("S3_BUCKET", "")
        headless = True

    if not email or not password:
        msg = "❌ Missing credentials: set SUPPLYNOTE_EMAIL and SUPPLYNOTE_PASSWORD"
        print(msg)
        return {"statusCode": 400, "body": msg}

    if not s3_bucket:
        msg = "❌ Missing S3_BUCKET environment variable"
        print(msg)
        return {"statusCode": 400, "body": msg}

    try:
        result = scrape_purchase_order_data(
            email, password, headless=headless, upload_to_s3=True, s3_bucket=s3_bucket, is_lambda=True
        )
        print("🎉 Purchase Order scraping completed successfully.")
        return {"statusCode": 200, "body": result}
    except Exception as e:
        print(f"❌ Lambda execution failed: {e}")
        return {"statusCode": 500, "body": f"Error: {e}"}

# ---------- Local runner ----------
def run_local(args):
    """
    Local runner to facilitate testing and debugging.
    """
    load_dotenv()

    email = args.email or os.getenv("SUPPLYNOTE_EMAIL", "")
    password = args.password or os.getenv("SUPPLYNOTE_PASSWORD", "")
    s3_bucket = args.s3_bucket or os.getenv("S3_BUCKET", "")

    if not email or not password:
        raise ValueError(
            "Please set SUPPLYNOTE_EMAIL and SUPPLYNOTE_PASSWORD (either env or CLI)."
        )

    upload_to_s3 = args.upload_to_s3 and bool(s3_bucket)

    if args.upload_to_s3 and not s3_bucket:
        print("⚠️ Warning: --upload-to-s3 specified but S3_BUCKET not set. Skipping S3 upload.")
        upload_to_s3 = False

    headless = args.headless
    print(f"🧪 Running purchase order scraper locally (headless={headless})...")
    print(f"📤 S3 Upload: {'Enabled' if upload_to_s3 else 'Disabled'}")

    result = scrape_purchase_order_data(
        email,
        password,
        headless=headless,
        base_url=args.base_url,
        upload_to_s3=upload_to_s3,
        s3_bucket=s3_bucket,
        is_lambda=False,
    )

    print("\n" + "=" * 50)
    print("✅ SCRAPING COMPLETED")
    print("=" * 50)
    if result.get("local_path"):
        print(f"📁 Local file: {result['local_path']}")
    if result.get("s3_path"):
        print(f"☁️ S3 location: {result['s3_path']}")
    print("=" * 50)


# ---------- CLI ----------
def build_argparser():
    parser = argparse.ArgumentParser(
        description="SupplyNote Purchase Order Scraper"
    )
    parser.add_argument("--email", help="SupplyNote email (overrides env)")
    parser.add_argument("--password", help="SupplyNote password (overrides env)")
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode locally",
    )
    parser.add_argument(
        "--base-url", default="https://supplynote.in", help="Base URL"
    )
    parser.add_argument(
        "--upload-to-s3",
        action="store_true",
        default=False,
        help="Upload Excel to S3 after scraping",
    )
    parser.add_argument(
        "--s3-bucket", help="S3 bucket for upload (overrides env S3_BUCKET)"
    )
    return parser


if __name__ == "__main__":
    parser = build_argparser()
    args = parser.parse_args()

    try:
        run_local(args)
    except Exception as exc:
        print(f"❌ Local run failed: {exc}")
        raise