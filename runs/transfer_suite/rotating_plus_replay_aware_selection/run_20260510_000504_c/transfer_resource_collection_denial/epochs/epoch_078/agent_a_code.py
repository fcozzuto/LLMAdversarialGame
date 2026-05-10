def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

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

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_target = None
    best_adv = None
    for (rx, ry) in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if best_adv is None or adv > best_adv or (adv == best_adv and sd < cheb(sx, sy, best_target[0], best_target[1])):
            best_adv = adv
            best_target = (rx, ry)

    if not best_target:
        tx, ty = 0, 0
    else:
        tx, ty = best_target

    def clamp(n, lo, hi):
        return lo if n < lo else hi if n > hi else n

    # Prefer taking tempo-winning resources; otherwise go nearest but avoid likely trap by obstacles.
    use_tempo = (best_adv is not None and best_adv >= 1) or len(resources) <= 2
    current_target_dist = cheb(sx, sy, tx, ty)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        sd = nd
        adv = od - sd
        obstacle_risk = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                obstacle_risk += 1
        score = 0
        if use_tempo:
            score = (adv * 20) - (nd * 3) - (obstacle_risk * 0.8)
        else:
            score = (-(nd * 4)) + (adv * 6) - (obstacle_risk * 0.8)
        if best_score is None or score > best_score or (score == best_score and nd < current_target_dist):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]