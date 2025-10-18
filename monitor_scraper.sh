#!/bin/bash
# Scraper Progress Monitor

echo "🔍 NYCU 課程綱要爬蟲 - 實時進度監控"
echo "=========================================="
echo ""

# Check if scraper is running
if ps aux | grep -q "outline_scraper_ultra_fast" | grep -v grep; then
    echo "✅ 爬蟲狀態: 運行中"
else
    echo "⏸️  爬蟲狀態: 未運行"
fi

echo ""
echo "📊 最新進度:"
tail -5 /tmp/outline_scraper_ultra.log | grep "已獲取" | tail -1

echo ""
echo "📈 速度統計:"
if [ -f /tmp/outline_scraper_ultra.log ]; then
    # Get first and last timestamp
    first_line=$(head -15 /tmp/outline_scraper_ultra.log | grep "已獲取" | head -1)
    last_line=$(tail -1 /tmp/outline_scraper_ultra.log | grep "已獲取")

    if [ ! -z "$first_line" ]; then
        echo "首次進度: $first_line"
    fi
    if [ ! -z "$last_line" ]; then
        echo "最新進度: $last_line"
    fi
fi

echo ""
echo "📁 輸出文件:"
if [ -f "/home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/outlines_all.json" ]; then
    file_size=$(du -h /home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/outlines_all.json | cut -f1)
    echo "✅ outlines_all.json: $file_size"
else
    echo "⏳ outlines_all.json: 尚未生成"
fi

echo ""
echo "📋 完成學期統計:"
if [ -f "/home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/.progress.json" ]; then
    cat /home/thc1006/dev/nycu_course_platform/scraper/data/course_outlines/.progress.json | grep -o '"[0-9]*-[0-9]*"' | wc -l
    echo "  個學期已完成"
fi

echo ""
echo "==========================================  "
echo "💡 監控命令:"
echo "  tail -f /tmp/outline_scraper_ultra.log"
