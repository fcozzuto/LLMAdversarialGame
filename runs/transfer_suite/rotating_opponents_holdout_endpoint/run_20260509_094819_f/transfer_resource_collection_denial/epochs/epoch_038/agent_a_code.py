def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Contention: choose a resource where we are relatively closer, factoring a tie-break urgency.
    contenders = []
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Higher is better: we want large (do - ds) to beat opponent; also include "distance to finish".
        score = (do - ds) * 10 - ds
        # Deterministic tie-break: prefer smaller coordinates if equal score.
        contenders.append((score, -ds, rx, ry))
    contenders.sort(reverse=True)
    _, _, tx, ty = contenders[0]

    # Greedy single-step toward chosen target, but if impossible, bias toward best alternative target.
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_here = cheb(nx, ny, tx, ty)
        # If moving doesn't improve much, consider local improvement against second-best contender.
        fallback_tx, fallback_ty = tx, ty
        if len(contenders) > 1:
            _, _, fallback_tx, fallback_ty = contenders[1]
        d_fb = cheb(nx, ny, fallback_tx, fallback_ty)

        # Deterministic evaluation: prioritize reducing distance to primary target; then to fallback; avoid wandering.
        eval_score = -d_here * 1000 - d_fb * 10 - (abs(nx - sx) + abs(ny - sy))
        cand = (eval_score, -cheb(sx, sy, tx, ty), nx, ny, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[4]), int(best[5])]