from spot_error import apply_action, make_scene, perceive

for i in range(8):
    img = make_scene(10_000 + i * 17 + len("mild_blur"), "mild_blur")
    before = perceive(img)
    after = perceive(apply_action(img, "sharpen_and_remeasure"))
    print(i, before["blur_variance"], after["blur_variance"])
