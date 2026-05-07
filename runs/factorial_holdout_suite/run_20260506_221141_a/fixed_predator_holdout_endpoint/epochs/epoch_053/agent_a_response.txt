def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))
        except Exception:
            pass
    if not resources:
        return [0, 0]

    def kdist(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    best = resources[0]
    best_score = -10**18
    for t in resources:
        sd = kdist((sx, sy), t)
        od = kdist((ox, oy), t)
        # Prefer resources where we can arrive earlier; if close, keep it immediate.
        score = (od - sd) * 1000 - sd
        # Slightly bias towards center-ish to reduce opponent cornering effects.
        cx, cy = w // 2, h // 2
        bias = - (abs(t[0] - cx) + abs(t[1] - cy))
        score += bias
        if score > best_score:
            best_score = score
            best = t

    tx, ty = best
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = (0, 0)
    best_md = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        d = kdist((nx, ny), (tx, ty))
        # Also ensure we don't step closer to a resource the opponent is likely already contesting:
        # if ties, take the move that maximizes (opp-self) for our chosen target's arrival.
        if d < best_md:
            best_md = d
            best_m = (dx, dy)
        elif d == best_md:
            cur_od = kdist((ox, oy), (tx, ty))
            cur_sd = d
            cand_score = (cur_od - cur_sd) * 1000 - cur_sd
            best_od = kdist((ox, oy), (tx, ty))
            best_sd = best_md
            best_score_m = (best_od - best_sd) * 1000 - best_sd
            if cand_score > best_score_m:
                best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]