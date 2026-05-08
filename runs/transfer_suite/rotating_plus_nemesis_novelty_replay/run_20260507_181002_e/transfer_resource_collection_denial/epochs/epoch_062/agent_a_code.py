def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            p = v.get("position", v.get("pos", None))
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                return int(p[0]), int(p[1])
        return default

    sx, sy = get_xy(observation.get("self_position", None), (0, 0))
    ox, oy = get_xy(observation.get("opponent_position", None), (sx, sy))

    obs = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))

    if not resources:
        return [0, 0]

    dx_dir = 1 if ox > sx else (-1 if ox < sx else 0)
    dy_dir = 1 if oy > sy else (-1 if oy < sy else 0)
    dominate_x = abs(ox - sx) >= abs(oy - sy)

    def score(cell):
        tx, ty = cell
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        if dominate_x:
            prog = (tx - sx) * dx_dir
        else:
            prog = (ty - sy) * dy_dir
        # Prefer grabbing resources sooner; add progress bias to counter row-sweep behavior.
        lead = od - sd
        return (lead, prog, -sd)

    tx, ty = max(resources, key=score)

    step_x = 0 if tx == sx else (1 if tx > sx else -1)
    step_y = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(step_x, step_y), (step_x, 0), (0, step_y), (step_x, -step_y), (0, 0)]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if free(nx, ny):
            return [int(mx), int(my)]

    return [0, 0]