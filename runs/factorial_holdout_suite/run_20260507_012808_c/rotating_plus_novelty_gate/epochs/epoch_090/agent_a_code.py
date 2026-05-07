def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    self_d = [(md(sx, sy, rx, ry), rx, ry) for rx, ry in resources]
    opp_d = [(md(ox, oy, rx, ry), rx, ry) for rx, ry in resources]
    sd, srx, sry = min(self_d, key=lambda t: (t[0], t[1], t[2]))
    od, orx, ory = min(opp_d, key=lambda t: (t[0], t[1], t[2]))
    diff = od - sd

    dx_options = (-1, 0, 1)
    dy_options = (-1, 0, 1)

    # Interceptor switch: if opponent is currently closer to their best resource, prioritize chasing them.
    chase = diff <= 0

    # Candidate scoring for one-step move.
    best = None
    for dx in dx_options:
        for dy in dy_options:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            if chase:
                # Step toward opponent, but don't walk into immediate loss: also favor distancing from opponent's reach.
                opp_step = md(nx, ny, ox, oy)
                # Evaluate resources available after move; prefer ones where we become closer than opponent.
                gain = 0
                for rx, ry in resources:
                    ds = md(nx, ny, rx, ry)
                    do = md(ox, oy, rx, ry)
                    if ds <= do:
                        # deterministic tie-break: prioritize closer to a winning resource
                        gain = max(gain, 100 - ds - 2 * do)
                key = (opp_step, -gain, nx, ny)
            else:
                # Go for best winning resource with a small incentive for nearer pickup.
                best_key = None
                for rx, ry in resources:
                    ds = md(nx, ny, rx, ry)
                    do = md(ox, oy, rx, ry)
                    key2 = (do - ds, -ds, rx, ry)
                    if best_key is None or key2 > best_key:
                        best_key = key2
                key = (best_key[0], best_key[1], -best_key[2], -best_key[3], nx, ny)
            if best is None or key < best:
                best = key
                bx, by = nx, ny

    return [bx - sx, by - sy]