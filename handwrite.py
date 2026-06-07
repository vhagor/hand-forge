import os
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
import inspect
from PIL import Image, ImageFont, ImageFilter
from handright import Template, handwrite


def generate_handwriting(text, font_path, output_name):
    upscale_factor = 6
    width, height = 2480 * upscale_factor, 3508 * upscale_factor

    template = Template(
        background=Image.new(mode="RGB", size=(width, height), color=(255, 255, 255)),
        font=ImageFont.truetype(font_path, size=100 * upscale_factor),
        line_spacing=120 * upscale_factor,
        fill=(15, 20, 30),
        left_margin=200 * upscale_factor,
        top_margin=250 * upscale_factor,
        right_margin=200 * upscale_factor,
        bottom_margin=250 * upscale_factor,

        line_spacing_sigma=8,
        font_size_sigma=15,
        word_spacing_sigma=10,
        perturb_x_sigma=20,
        perturb_y_sigma=20,
        perturb_theta_sigma=0.12,
    )

    tag = f"[pid={os.getpid()} {os.path.basename(font_path)}]"
    print(f"{tag} 开始渲染...", flush=True)

    pages = handwrite(text, template)
    pdf_pages = []
    saved_files = []

    for i, page in enumerate(pages):
        page = page.filter(ImageFilter.MinFilter(size=5))
        page = page.filter(ImageFilter.GaussianBlur(radius=3))

        final_page = page.resize((2480, 3508), resample=Image.LANCZOS)

        file_path = f"{output_name}_style_{i}.png"
        final_page.save(file_path, optimize=True)
        saved_files.append(file_path)
        print(f"{tag} 已保存 {file_path}", flush=True)

        # pdf_pages.append(final_page)

    pdf_path = None
    if pdf_pages:
        pdf_path = f"{output_name}_printable.pdf"
        pdf_pages[0].save(
            pdf_path,
            "PDF",
            resolution=300.0,
            save_all=True,
            append_images=pdf_pages[1:],
        )
        print(f"{tag} PDF 已生成: {pdf_path}", flush=True)

    return {
        "font": font_path,
        "pages": len(saved_files),
        "files": saved_files,
        "pdf": pdf_path,
    }


def _worker(args):
    """进程池入口：包一层异常捕获，避免单个字体挂掉拖垮整批。"""
    text, font_path, output_name = args
    try:
        return ("ok", font_path, generate_handwriting(text, font_path, output_name))
    except Exception as e:
        return ("error", font_path, f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


# ================= 配置区 =================
if __name__ == "__main__":
    contents = [
        # inspect.cleandoc("""
        #     谢宏力：
        #         李居奇同志政治立场坚定，思想积极向上，多位同志反映，该同志认真学习党的理论方针政策，积极参与支部组织的学习活动，思想上积极向党组织靠拢。他学习刻苦，科研能力突出，作风朴实，团结同学，班级同学评价该同志待人真诚，乐于助人，积极参与班级事务和志愿活动，群众基础较好。他遵守纪律，严于律己，支部党员指出，该同志能够严格遵守校规校纪和党的组织纪律，日常行为规范，起到了一定模范带头作用。
        #         然而，李居奇同志也存在着些许不足，理论学习系统性有待加强，有同志建议，李居奇同志在理论学习上虽然积极，但有时理解不够深入，建议结合实际多思考、多总结。组织表达能力需进一步提升，部分同学提出，该同志在公开场合发言时略显紧张，表达不够清晰，建议多参与讨论和演讲类活动，提升表达能力。工作方法需更灵活，有同志指出，在处理多项任务时，偶尔表现出一定的急躁情绪，建议学会更好统筹安排，提高应变能力。
        # """)
        # inspect.cleandoc("""
        # 钱乾霖：
        #     李居奇同志政治信念坚定，思想积极进取，大家一致认为，该同志日常主动学习党的创新理论，积极响应支部号召，入党动机纯洁，集体责任感强。他学习态度端正，科研产出丰富，指导老师和同门反映，其在科研工作中具备很强的主动性和创新意识，遇到难题不退缩。他平易近人，乐于助人，班级同学表示，该同志待人接物和善，经常热心帮助遇到困难的同学，团队协作意识强。他纪律观念强，严于律己，支部反映，其严格遵守党纪校规，不骄不躁，展现了良好的学生党员风貌。
        #     不过，李居奇同志还有一定的提升空间，首先，他理论联系实际能力有待加强：有同志建议其工作抗压与灵活度需改善：遇到项目瓶颈且时间紧迫时，有时会表现出轻微的焦虑情绪，建议学会更好地调节心态并优化工作方法。
        # """)
        # inspect.cleandoc("""
        # 和之阳：
        #     李居奇同志政治立场鲜明，思想端正积极，周围同志评价，该同志政治站位高，积极参与各类党团学习活动，思想汇报深刻真实，有着向党组织靠拢的强烈意愿。钻研学习刻苦，科研成果初显，实验室同学认为，该同志科研基础扎实，工作勤奋，能够在团队合作中发挥关键作用。他为人低调务实，团结同学，大家反映该同志不计较个人得失，乐于为班级和实验室同学服务，人际关系融洽。
        #     但在某些方面，李居奇同志仍需努力，例如，公众表达与展示能力欠佳，在进行工作汇报时，临场应变和语言感染力不足，建议多参加演讲或答辩活动积累经验。
        # """)
        # inspect.cleandoc("""
        # 刘健：
        #     李居奇同志政治素养良好，思想追求进步：多位同志反映，该同志平时注重自我思想武装，主动了解党的政策方针，思想汇报态度诚恳，集体认同感强。学习勤奋刻苦，科研态度严谨：实验室同伴表示，李居奇同志在学术研究上精益求精，动手能力强，能够出色完成导师交办的各项科研任务。为人热情真诚，群众口碑良好：班级同学评价其乐于奉献，积极参与各项志愿服务活动，与大家打成一片。遵纪守法，自我约束力强：支部认为该同志规矩意识牢固，作风正派，起到了积极的带头作用。
        #     与此同时，李居奇同志也存在一些缺点。理论学习的钻研精神需提升：部分同志指出，其对某些深刻的理论问题理解不够透彻，建议加强原著原文的阅读，提升英文阅读水平。
        # """)
        #     inspect.cleandoc("""
        # 郭春夏：
        #     李居奇同志政治方向明确，思想觉悟不断提升，群众反映，该同志积极拥护党的领导，认真贯彻支部决议，有较强的思想上进心和集体服务意识。该同志专业基础扎实，科研作风踏实，实验室成员指出，李居奇同志对待科研任务一丝不苟，他纪律严明，作风优良，支部同志表示，该同志严格遵守各项纪律要求，生活作风简朴，品行端正。
        #     客观而言，李居奇同志还有待完善之处。理论学习的深度和广度有待拓展，有同志反映，其在理论学习上往往停留在完成任务层面，缺乏主动的深度探究。
        #     """)
        #     inspect.cleandoc("""
        # 那田印：
        #     李居奇同志政治素质过硬，思想态度端正积极，多名同志反映，该同志认真学习习近平新时代中国特色社会主义思想，政治立场坚定，入党动机明确。科研勤奋刻苦，为人随和朴实，群众基础深厚：班级同学评价其热心肠，积极参与班级建设，与周围同学建立了深厚的友谊。规矩意识强，严格自律：支部评价该同志能够严格恪守各项纪律，发挥了较好的先锋模范作用。
        #     但也存在以下不足，工作方法的科学性有待提升，有同志建议，在同时处理多项任务时，该同志偶尔缺乏轻重缓急的合理规划，导致情绪波动，需提升综合统筹能力。
        #     """)
        #     inspect.cleandoc("""
        # 沈致远：
        #     李居奇同志政治素质过硬，思想态度端正积极，多名同志反映，该同志认真学习习近平新时代中国特色社会主义思想，政治立场坚定，入党动机明确。科研勤奋刻苦，为人随和朴实，群众基础深厚，班级同学评价其热心肠，积极参与班级建设，与周围同学建立了深厚的友谊。
        #     但也存在以下不足，性格略显急躁，做事过于追求完美，这些有待提升，有同志建议，该同志偶尔缺乏轻重缓急的合理规划，导致情绪波动，需提升综合统筹能力。
        #     """)
        # inspect.cleandoc("""
        #    徐兆桦：
        #       李居奇同志政治站位正确，思想作风优良，群众一致反映，该同志积极学习党的各项政策，思想纯洁，集体荣誉感和责任心强。科研作风严谨，专业技能扎实，作为实验室同门表示，该同志在科研实践中敢于吃苦，善于钻研。他为人真诚低调，在同学中享有较高威信。他纪律严明，道德品质高尚，支部反映该同志能够模范遵守党的纪律和学校规章，起到标杆作用。不过，李居奇同志也存在一些短板。例如理论知识吸收不够内化，有同志指出，该同志在政治理论的融会贯通上稍显欠缺，理论和实践结合不够紧密，建议多参与社会实践活动，将理论知识应用到实际工作中。
        #     """)

        inspect.cleandoc("""
            任杰：
            李居奇同志政治觉悟高，思想纯洁向上，大家反映，该同志对党忠诚，积极主动学习党的历史和理论方针，入党态度坚决，思想端正。学习认真刻苦，科研表现优异，实验室同门表示，李居奇同志具备扎实的专业功底和浓厚的科研兴趣，在项目中起到了骨干支撑作用。为人宽厚踏实，乐于服务群众，班级同学评价该同志不骄不躁，经常主动承担班级脏活累活，群众基础扎实。他纪律观念牢固，自我约束严密，支部认为该同志能够严格按照党员标准要求自己，无任何违纪违规行为。
            客观来看，李居奇同志尚有以下不足。例如公开场合沟通表达能力稍弱，不少同学建议，该同志在大型会议或公开场合发言时不够活跃，需要克服紧张心理，提升表达能力。
        """)

    ]

    font_files = [
        # "fonts/1.ttf",
        # "fonts/2.ttf",
        # "fonts/3.ttf",
        # "fonts/4.ttf",
        # "fonts/5.ttf",
        # "fonts/6.ttf",
        # "fonts/7.ttf",
        # "fonts/8.ttf",
        "fonts/9.ttf",
    ]

    # 并发度：默认 = 字体数与（CPU 核数 - 1）取较小者，至少为 1
    # 留一个核给系统，避免整机卡顿；想吃满就改成 os.cpu_count()
    MAX_WORKERS = max(1, min(len(font_files), (os.cpu_count() or 2) - 1))

    os.makedirs("output", exist_ok=True)

    # 准备任务列表：跳过不存在的字体
    tasks = []
    for idx, f_path in enumerate(font_files):
        if os.path.exists(f_path):
            tasks.append((contents[0], f_path, f"output/handwriting_v{idx}"))
        else:
            print(f"跳过：未找到字体文件 {f_path}")

    if not tasks:
        print("没有可用的字体文件")
        raise SystemExit(0)

    print(f"\n共 {len(tasks)} 个字体任务，使用 {MAX_WORKERS} 个并发进程\n")
    t0 = time.time()

    ok_count = 0
    err_count = 0
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_worker, t): t[1] for t in tasks}
        for fut in as_completed(futures):
            status, font_path, payload = fut.result()
            if status == "ok":
                ok_count += 1
                print(f"\n✓ {os.path.basename(font_path)} 完成："
                      f"生成 {payload['pages']} 页，PDF={payload['pdf']}\n", flush=True)
            else:
                err_count += 1
                print(f"\n✗ {os.path.basename(font_path)} 失败：\n{payload}\n", flush=True)

    dt = time.time() - t0
    print(f"\n全部完成，用时 {dt:.1f}s   成功 {ok_count}  失败 {err_count}")
