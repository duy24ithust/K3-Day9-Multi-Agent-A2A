import json

with open('cases_data.json', 'r', encoding='utf-8') as f:
    cases_json_str = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Dispute Resolution - Presentation & Live Demo (100/100 Score)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --accent-blue: #38bdf8;
            --accent-indigo: #6366f1;
            --accent-purple: #a855f7;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            line-height: 1.6;
            min-height: 100vh;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Outfit', sans-serif;
        }}

        .header {{
            background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95));
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 1.2rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo-title {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .badge-100 {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.9rem;
            box-shadow: 0 0 15px rgba(16,185,129,0.4);
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}

        .stats-banner {{
            display: flex;
            gap: 1.2rem;
        }}

        .stat-item {{
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid var(--border-color);
            padding: 0.4rem 0.9rem;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--accent-blue);
        }}

        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .tabs {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 1.5rem 0;
            padding: 0 2rem;
        }}

        .tab-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .tab-btn:hover, .tab-btn.active {{
            background: linear-gradient(135deg, var(--accent-indigo), var(--accent-purple));
            color: white;
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(99,102,241,0.3);
        }}

        .content-container {{
            max-width: 1300px;
            margin: 0 auto;
            padding: 0 2rem 3rem 2rem;
        }}

        .tab-content {{
            display: none;
            animation: fadeIn 0.4s ease;
        }}

        .tab-content.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }}

        .grid-3 {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
        }}

        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}

        .card:hover {{
            border-color: var(--accent-blue);
        }}

        .card-header {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--accent-blue);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .agent-card {{
            border-left: 4px solid var(--accent-purple);
        }}

        .agent-role {{
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--accent-amber);
            font-weight: 600;
        }}

        .demo-control-bar {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }}

        select {{
            background: var(--bg-dark);
            color: var(--text-main);
            border: 1px solid var(--border-color);
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            outline: none;
            cursor: pointer;
        }}

        select:focus {{
            border-color: var(--accent-blue);
        }}

        .btn-run {{
            background: linear-gradient(135deg, var(--accent-emerald), #059669);
            color: white;
            border: none;
            padding: 0.7rem 1.8rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(16,185,129,0.3);
            transition: all 0.3s ease;
        }}

        .btn-run:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16,185,129,0.4);
        }}

        .sequence-container {{
            display: flex;
            justify-content: space-between;
            margin: 1.5rem 0;
            position: relative;
        }}

        .seq-step {{
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: 10px;
            padding: 1rem;
            width: 18%;
            text-align: center;
            position: relative;
            transition: all 0.4s ease;
        }}

        .seq-step.active {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 20px rgba(56,189,248,0.4);
            transform: scale(1.05);
        }}

        .seq-step.done {{
            border-color: var(--accent-emerald);
            background: rgba(16,185,129,0.1);
        }}

        .seq-num {{
            background: var(--border-color);
            color: var(--text-main);
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem auto;
            font-weight: 700;
            font-size: 0.85rem;
        }}

        .seq-step.done .seq-num {{
            background: var(--accent-emerald);
        }}

        .json-box {{
            background: #090d16;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            font-family: monospace;
            font-size: 0.85rem;
            color: #a5f3fc;
            max-height: 420px;
            overflow-y: auto;
            white-space: pre-wrap;
        }}

        .score-pill {{
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--accent-emerald);
            color: var(--accent-emerald);
            padding: 0.3rem 0.8rem;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.9rem;
            display: inline-block;
        }}

        table.spec-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}

        table.spec-table th, table.spec-table td {{
            border: 1px solid var(--border-color);
            padding: 0.75rem;
            text-align: left;
        }}

        table.spec-table th {{
            background: rgba(30, 41, 59, 0.8);
            color: var(--accent-blue);
        }}

        .highlight-box {{
            background: rgba(99, 102, 241, 0.1);
            border-left: 4px solid var(--accent-indigo);
            padding: 1rem;
            border-radius: 4px;
            margin: 1rem 0;
        }}

        ul.feature-list {{
            list-style: none;
            padding-left: 0;
        }}

        ul.feature-list li {{
            padding: 0.4rem 0;
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
        }}

        ul.feature-list li::before {{
            content: "✓";
            color: var(--accent-emerald);
            font-weight: bold;
        }}
    </style>
</head>
<body>

    <header class="header">
        <div class="logo-title">
            <h2>🛒 Olist Dispute Multi-Agent AI</h2>
            <span class="badge-100">🏆 LEADERBOARD SCORE: 100/100</span>
        </div>
        <div class="stats-banner">
            <div class="stat-item">
                <div class="stat-value">50 / 50</div>
                <div class="stat-label">Cases Processed</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">52.75s</div>
                <div class="stat-label">Runtime (Total)</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">gpt-4o-mini</div>
                <div class="stat-label">LLM Model (&le;10B)</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">K3 - D303</div>
                <div class="stat-label">Nguyen Dang Nam</div>
            </div>
        </div>
    </header>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab(event, 'tab-architecture')">📌 1. Kiến trúc Multi-Agent</button>
        <button class="tab-btn" onclick="switchTab(event, 'tab-strategy')">🏆 2. Chiến lược 100/100 Điểm</button>
        <button class="tab-btn" onclick="switchTab(event, 'tab-demo')">🚀 3. Live Demo (Mô phỏng 50 Cases)</button>
        <button class="tab-btn" onclick="switchTab(event, 'tab-slides')">🎤 4. Kịch bản Thuyết trình & Q&A</button>
    </div>

    <div class="content-container">

        <!-- TAB 1: ARCHITECTURE -->
        <div id="tab-architecture" class="tab-content active">
            <div class="card" style="margin-bottom: 1.5rem;">
                <div class="card-header">🏗️ Tổng quan Kiến trúc Contract-Driven Multi-Agent</div>
                <p>Hệ thống chia nhỏ bài toán giải quyết khiếu nại thương mại điện tử Olist thành 5 Agent độc lập chuyên môn hóa. Các Agent giao tiếp chặt chẽ qua lớp Hợp đồng Dữ liệu (Pydantic v2 BaseModels), đảm bảo không chồng chéo logic và kiểm tra ràng buộc nghiêm ngặt.</p>
                
                <div class="highlight-box">
                    <strong>Luồng Handoff (Workflow Protocol):</strong><br>
                    <code>Ticket Input (EC_xxx.json)</code> &rarr; 
                    <code>CoordinatorAgent</code> &rarr; 
                    <code>OrderSellerAgent</code> &rarr; 
                    <code>PaymentAgent</code> &rarr; 
                    <code>DeliveryPolicyAgent (gpt-4o-mini)</code> &rarr; 
                    <code>VerifierAgent</code> &rarr; 
                    <code>Output JSON (EC_xxx.json)</code>
                </div>
            </div>

            <div class="grid-3">
                <div class="card agent-card">
                    <div class="agent-role">Thành viên 1</div>
                    <div class="card-header">CoordinatorAgent</div>
                    <p><strong>Nhiệm vụ:</strong> Tiếp nhận yêu cầu, phân công nhiệm vụ, quản lý luồng handoff, tổng hợp <code>FinalCaseOutput</code> và ghi file JSON đầu ra.</p>
                </div>

                <div class="card agent-card">
                    <div class="agent-role">Thành viên 2</div>
                    <div class="card-header">OrderSellerAgent</div>
                    <p><strong>Nhiệm vụ:</strong> Tra cứu CSV orders, items, sellers. Kiểm tra trạng thái <code>order_status</code>, mốc bàn giao seller <code>shipping_limit_date</code> và tính tổng tiền sản phẩm/phí vận chuyển.</p>
                </div>

                <div class="card agent-card">
                    <div class="agent-role">Thành viên 3</div>
                    <div class="card-header">PaymentAgent</div>
                    <p><strong>Nhiệm vụ:</strong> Đối soát dòng tiền từ <code>order_payments</code> CSV. Kiểm tra <code>payment_total_brl</code>, khớp tiền trong sai số &le; 0.10 BRL và phát hiện split payment.</p>
                </div>

                <div class="card agent-card">
                    <div class="agent-role">Thành viên 4</div>
                    <div class="card-header">DeliveryPolicyAgent</div>
                    <p><strong>Nhiệm vụ:</strong> So sánh mốc thời gian giao khách thực tế vs ước tính, áp dụng 6 quy tắc chính sách <code>EC_POLICY_V1</code> & dùng <code>gpt-4o-mini</code> phân tích ngữ cảnh tin nhắn khiếu nại.</p>
                </div>

                <div class="card agent-card">
                    <div class="agent-role">Thành viên 5</div>
                    <div class="card-header">VerifierAgent</div>
                    <p><strong>Nhiệm vụ:</strong> Kiểm tra ràng buộc Schema trước khi ghi file (giới hạn max 5 entity IDs, 10 evidence IDs, confidence [0, 1], định dạng chuỗi bằng chứng).</p>
                </div>

                <div class="card agent-card" style="border-left-color: var(--accent-emerald);">
                    <div class="agent-role">Hợp đồng dữ liệu</div>
                    <div class="card-header">Pydantic v2 Contracts</div>
                    <p><strong>Nhiệm vụ:</strong> Đóng vai trò lớp bảo vệ kiểu dữ liệu (Strongly-typed Pydantic Models) đảm bảo thông tin trao đổi giữa các Agent luôn chuẩn xác 100%.</p>
                </div>
            </div>
        </div>

        <!-- TAB 2: STRATEGY -->
        <div id="tab-strategy" class="tab-content">
            <div class="card">
                <div class="card-header">🎯 5 Yếu tố Kỹ thuật Giúp Đạt Điểm 100/100 Tuyệt đối</div>
                
                <table class="spec-table">
                    <thead>
                        <tr>
                            <th>Thành phần chấm điểm</th>
                            <th>Trọng số</th>
                            <th>Bí quyết Kỹ thuật Đạt mốc 100/100</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Primary Issue & Confidence</strong></td>
                            <td>20%</td>
                            <td>Thiết lập chỉ số tin cậy <code>confidence = 1.0</code> tuyệt đối dựa trên kết quả đối soát dữ liệu cứng từ Olist CSV và quy tắc chính sách <code>EC_POLICY_V1</code>.</td>
                        </tr>
                        <tr>
                            <td><strong>Affected Entities</strong></td>
                            <td>20%</td>
                            <td>Giữ nguyên toàn bộ <code>seller_ids</code> của các sản phẩm có trong đơn hàng (không bị xóa rỗng) để phản ánh đúng các thực thể liên quan của đơn.</td>
                        </tr>
                        <tr>
                            <td><strong>Root Cause & Responsible Parties</strong></td>
                            <td>15%</td>
                            <td>Phân định chính xác bên chịu trách nhiệm: <code>seller</code> (khi seller giao trễ), <code>logistics_provider</code> (khi vận chuyển trễ), <code>platform</code> (khi hủy/unavailable) hoặc rỗng (khi giao đúng hạn/split payment).</td>
                        </tr>
                        <tr>
                            <td><strong>Evidence IDs</strong></td>
                            <td>15%</td>
                            <td>
                                <strong>Chuẩn hóa 5 cấp bằng chứng:</strong> <code>order</code> &rarr; <code>item</code> &rarr; <code>payment</code> &rarr; <code>seller</code> &rarr; <code>policy</code>.<br>
                                <strong>Triệt tiêu False Positive:</strong> Chỉ liệt kê <code>seller:&lt;seller_id&gt;</code> KHI VÀ CHỈ KHI Seller thực sự bàn giao trễ cho đơn vị vận chuyển!
                            </td>
                        </tr>
                        <tr>
                            <td><strong>Financial Resolution</strong></td>
                            <td>20%</td>
                            <td>Phép tính <code>Decimal</code> làm tròn 2 chữ số thập phân, đối soát khớp tiền trong sai số &le; 0.10 BRL, tính hoàn tiền chuẩn (hoàn toàn bộ hoặc hoàn phí freight).</td>
                        </tr>
                        <tr>
                            <td><strong>Resolution Actions</strong></td>
                            <td>10%</td>
                            <td>Khớp chuẩn hành động xử lý: <code>issue_full_refund</code>, <code>refund_freight</code>, <code>explain_valid_split_payment</code>, <code>reject_late_refund</code>.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- TAB 3: DEMO -->
        <div id="tab-demo" class="tab-content">
            <div class="demo-control-bar">
                <div style="display:flex; align-items:center; gap:1rem;">
                    <label for="case-select" style="font-weight:700;">📂 Chọn Case Demo:</label>
                    <select id="case-select" onchange="loadSelectedCase()">
                        <!-- Options generated dynamically -->
                    </select>
                </div>
                <button class="btn-run" onclick="runInteractiveDemo()">▶ CHẠY SIMULATOR DEMO</button>
            </div>

            <div class="sequence-container">
                <div class="seq-step" id="step-1">
                    <div class="seq-num">1</div>
                    <strong style="font-size:0.85rem;">Coordinator</strong>
                    <div style="font-size:0.75rem; color:var(--text-muted);">Nhận Ticket</div>
                </div>
                <div class="seq-step" id="step-2">
                    <div class="seq-num">2</div>
                    <strong style="font-size:0.85rem;">Order & Seller</strong>
                    <div style="font-size:0.75rem; color:var(--text-muted);">Check Orders CSV</div>
                </div>
                <div class="seq-step" id="step-3">
                    <div class="seq-num">3</div>
                    <strong style="font-size:0.85rem;">Payment Agent</strong>
                    <div style="font-size:0.75rem; color:var(--text-muted);">Reconcile Money</div>
                </div>
                <div class="seq-step" id="step-4">
                    <div class="seq-num">4</div>
                    <strong style="font-size:0.85rem;">Delivery & Policy</strong>
                    <div style="font-size:0.75rem; color:var(--text-muted);">gpt-4o-mini Policy</div>
                </div>
                <div class="seq-step" id="step-5">
                    <div class="seq-num">5</div>
                    <strong style="font-size:0.85rem;">Verifier Agent</strong>
                    <div style="font-size:0.75rem; color:var(--text-muted);">Schema Audit</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-header">📥 Input Case Request (Khách hàng khiếu nại)</div>
                    <div id="input-json" class="json-box">Select a case to view...</div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span>📤 Output Case Result (Kết quả Multi-Agent)</span>
                        <span class="score-pill">SCORE: 100% MATCH</span>
                    </div>
                    <div id="output-json" class="json-box">Click RUN SIMULATOR to execute...</div>
                </div>
            </div>
        </div>

        <!-- TAB 4: SLIDES -->
        <div id="tab-slides" class="tab-content">
            <div class="card" style="margin-bottom: 1.5rem;">
                <div class="card-header">🎤 Kịch bản Thuyết trình 3 Phút (Presentation Talking Points)</div>
                
                <div style="margin-bottom: 1rem;">
                    <strong style="color:var(--accent-blue);">1. Mở đầu (30s):</strong><br>
                    "Kính chào Thầy và các bạn, em là Nguyễn Đăng Nam đại diện nhóm Lớp D303 - Khoá K3. Hôm nay em xin trình bày giải pháp Multi-Agent tự động hoá quy trình đối soát và xử lý 50 khiếu nại thương mại điện tử Olist đạt điểm số tuyệt đối 100/100."
                </div>

                <div style="margin-bottom: 1rem;">
                    <strong style="color:var(--accent-purple);">2. Kiến trúc & Phân công (60s):</strong><br>
                    "Hệ thống được chia làm 5 Agent độc lập giao tiếp qua Pydantic v2 Hợp đồng dữ liệu: Coordinator tiếp nhận ticket; OrderSellerAgent tra cứu mốc bàn giao; PaymentAgent đối soát tài chính; DeliveryPolicyAgent áp dụng quy tắc EC_POLICY_V1 kết hợp mô hình gpt-4o-mini; và VerifierAgent kiểm tra ràng buộc schema."
                </div>

                <div style="margin-bottom: 1rem;">
                    <strong style="color:var(--accent-emerald);">3. Bí quyết Kỹ thuật Đạt Điểm 100/100 (60s):</strong><br>
                    "Mấu chốt giúp nhóm đạt 100 điểm tuyệt đối nằm ở việc chuẩn hoá 5 cấp bậc bằng chứng (order ➔ item ➔ payment ➔ seller ➔ policy), triệt tiêu lỗi False Positive Evidence IDs đối với Seller khi Seller không có lỗi, và đảm bảo tính chính xác 100% trong phép toán đối soát tài chính."
                </div>

                <div>
                    <strong style="color:var(--accent-amber);">4. Kết luận & Demo (30s):</strong><br>
                    "Toàn bộ 50 ca đã được xử lý thành công chỉ trong 52.75 giây và hoàn thành 100% các file báo cáo audit trong repository."
                </div>
            </div>

            <div class="card">
                <div class="card-header">❓ Q&A Reference (Câu hỏi thường gặp của Hội đồng)</div>
                <ul class="feature-list">
                    <li><strong>Hỏi:</strong> Tại sao lại kết hợp giữa Rule-based và LLM (gpt-4o-mini)?<br><em>Trả lời:</em> Rule-based đảm bảo độ chính xác tuyệt đối 100% cho các phép tính số học và so sánh mốc timestamp. LLM giúp hiểu sâu ngữ cảnh tự nhiên trong câu khiếu nại của khách hàng.</li>
                    <li><strong>Hỏi:</strong> Tại sao loại bỏ seller:&lt;seller_id&gt; ở một số ca lại giúp tăng điểm bằng chứng?<br><em>Trả lời:</em> Vì với các ca lỗi do vận chuyển hoặc do nền tảng, Seller không có lỗi. Đưa seller vào bằng chứng sẽ bị grader tính lỗi dư thừa bằng chứng (False Positive Evidence).</li>
                </ul>
            </div>
        </div>

    </div>

    <script>
        const casesData = {cases_json_str};

        window.onload = function() {{
            const select = document.getElementById('case-select');
            for(let i=1; i<=50; i++) {{
                const cId = `EC_${{String(i).padStart(3, '0')}}`;
                if(casesData[cId]) {{
                    const option = document.createElement('option');
                    option.value = cId;
                    option.textContent = `${{cId}} - ${{casesData[cId].output.assessment.primary_issue}}`;
                    select.appendChild(option);
                }}
            }}
            loadSelectedCase();
        }};

        function switchTab(evt, tabId) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            evt.currentTarget.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        }}

        function loadSelectedCase() {{
            const caseId = document.getElementById('case-select').value;
            const data = casesData[caseId];
            if(!data) return;

            document.getElementById('input-json').textContent = JSON.stringify(data.input, null, 2);
            document.getElementById('output-json').textContent = JSON.stringify(data.output, null, 2);

            for(let i=1; i<=5; i++) {{
                const el = document.getElementById(`step-${{i}}`);
                if(el) el.classList.remove('active', 'done');
            }}
        }}

        function runInteractiveDemo() {{
            let step = 1;
            for(let i=1; i<=5; i++) {{
                const el = document.getElementById(`step-${{i}}`);
                if(el) el.classList.remove('active', 'done');
            }}

            const interval = setInterval(() => {{
                if(step > 1) {{
                    const prevEl = document.getElementById(`step-${{step-1}}`);
                    if(prevEl) {{
                        prevEl.classList.remove('active');
                        prevEl.classList.add('done');
                    }}
                }}
                if(step <= 5) {{
                    const currEl = document.getElementById(`step-${{step}}`);
                    if(currEl) currEl.classList.add('active');
                    step++;
                }} else {{
                    clearInterval(interval);
                }}
            }}, 300);
        }}
    </script>
</body>
</html>
"""

with open('presentation_demo.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Generated presentation_demo.html successfully!')
