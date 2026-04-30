def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res.append((int(p[0]), int(p[1])))

    my = (sx, sy)
    opp = (ox, oy)
    if res:
        my_near = min(res, key=lambda r: dist(my, r))
        op_near = min(res, key=lambda r: dist(opp, r))
    else:
        my_near = None
        op_near = None

    best = (0, 0)
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        here = (nx, ny)

        if res:
            my_d = min(dist(here, r) for r in res)
            op_d = min(dist(opp, r) for r in res)
            lead = op_d - my_d  # positive if we are closer to some resource than opponent
            on_res = 1 if here in set(res) else 0
            # Encourage moving toward our nearest resource more strongly,
            # but keep an eye on contesting the resource the opponent is likely closest to.
            toward_my = dist(here, my_near) if my_near is not None else 0
            toward_op_target = dist(here, op_near) if op_near is not None else 0
            # Also keep some separation to avoid easy grabs.
            sep = dist(here, opp)

            s = 1200 * on_res
            s += 80 * lead
            s += -3.5 * my_d
            s += 0.8 * sep
            s += -0.9 * toward_my
            s += -0.25 * toward_op_target * (1 if op_d <= my_d + 1 else 0)
        else:
            center = (w // 2, h // 2)
            my_d = dist(here, center)
            sep = dist(here, opp)
            s = -1.2 * my_d + 0.35 * sep

        if s > best_s:
            best_s = s
            best = (dx, dy)

    return [int(best[0]), int(best[1])]