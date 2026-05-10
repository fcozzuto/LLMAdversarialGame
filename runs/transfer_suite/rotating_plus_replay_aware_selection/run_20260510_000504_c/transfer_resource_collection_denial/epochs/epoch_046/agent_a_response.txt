def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    width = int(observation.get("grid_width") or 8)
    height = int(observation.get("grid_height") or 8)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obstacles.add((int(p["position"][0]), int(p["position"][1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < width and 0 <= y < height

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def man(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    scored = []
    for rx, ry in resources:
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; penalize those opponent is closer to.
        val = du - 0.85 * do + 0.03 * man(sx, sy, rx, ry)
        scored.append((val, rx, ry))
    scored.sort(key=lambda t: (t[0], t[1], t[2]))
    tx, ty = scored[0][1], scored[0][2]

    dx_raw = 0 if tx == sx else (1 if tx > sx else -1)
    dy_raw = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Bias toward stepping in the direction of the target.
            step_toward = (abs(tx - nx) < abs(tx - sx) or abs(ty - ny) < abs(ty - sy))
            toward_score = 0
            if dx == dx_raw: toward_score += 2
            if dy == dy_raw: toward_score += 2
            # Tie-break: avoid squares closer to opponent when we are behind.
            du_next = cheb(nx, ny, tx, ty)
            do_next = cheb(nx, ny, ox, oy)
            behind = 1 if cheb(sx, sy, tx, ty) > cheb(ox, oy, tx, ty) else 0
            score = du_next + (0.12 * behind) * do_next - 0.05 * toward_score - (0.02 if step_toward else 0)
            candidates.append((score, dx, dy))

    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    if not candidates:
        return [0, 0]
    return [int(candidates[0][1]), int(candidates[0][2])]