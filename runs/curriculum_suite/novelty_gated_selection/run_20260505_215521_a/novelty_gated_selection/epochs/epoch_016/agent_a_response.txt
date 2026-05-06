def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        # Drift to increase distance from opponent cornering
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obst:
                    val = (md(nx, ny, ox, oy), -nx, -ny)
                    if best is None or val > best[0]:
                        best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Pick a resource where we are relatively closer than opponent
    best_res = None
    for rx, ry in resources:
        if not (isinstance(rx, (int, float)) and isinstance(ry, (int, float))):
            continue
        rx, ry = int(rx), int(ry)
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        rel = od - sd  # larger => more our advantage
        cand = (rel, -sd, rx, ry)
        if best_res is None or cand > best_res[0]:
            best_res = (cand, rx, ry)

    _, tx, ty = best_res if best_res else (None, sx, sy)

    # Choose move that improves relative advantage toward target
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (inb(nx, ny) and (nx, ny) not in obst):
                continue
            sd2 = md(nx, ny, tx, ty)
            od2 = md(ox, oy, tx, ty)
            rel2 = od2 - sd2
            # Also avoid moves that move us closer to opponent (helps against denial)
            opp_d = md(nx, ny, ox, oy)
            key = (rel2, -sd2, opp_d, -abs(dx), -abs(dy), nx, ny)
            if best is None or key > best[0]:
                best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]