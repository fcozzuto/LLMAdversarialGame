def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def best_move_for_target(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            # Try single-axis move deterministically
            if (sx + dx, sy) not in obstacles:
                nx, ny = sx + dx, sy
            elif (sx, sy + dy) not in obstacles:
                nx, ny = sx, sy + dy
            else:
                nx, ny = sx, sy
        return [nx - sx, ny - sy]

    # Prefer resources we can reach no later than opponent; otherwise deny by minimizing opponent lead.
    lead_candidates = []
    tie_candidates = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            # primary: how much earlier or equal we are; secondary: smaller ds; tertiary: prefer higher x/y deterministically
            lead_candidates.append(((do - ds) * 1000 - ds, -rx, -ry, (rx, ry)))
        else:
            # we are slower: minimize (ds - do); also keep ds small to potentially retarget
            tie_candidates.append((-(ds - do) * 1000 - ds, -rx, -ry, (rx, ry)))

    if lead_candidates:
        lead_candidates.sort(reverse=True)
        tx, ty = lead_candidates[0][3]
    else:
        tie_candidates.sort(reverse=True)
        tx, ty = tie_candidates[0][3]

    return best_move_for_target(tx, ty)