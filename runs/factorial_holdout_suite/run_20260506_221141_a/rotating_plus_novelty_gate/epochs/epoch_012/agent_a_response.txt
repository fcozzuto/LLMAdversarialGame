def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        ax = abs(x1 - x2)
        ay = abs(y1 - y2)
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def best_target():
        rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
        best = None
        tx_best = ty_best = 0
        for p in resources:
            tx, ty = int(p[0]), int(p[1])
            if not valid(tx, ty):
                continue
            md = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - md  # >0 means we arrive no later
            # Strongly prefer resources we can reach earlier; otherwise prefer those opponent is far from.
            # When resources are scarce, prioritize immediate closeness for certainty.
            scarcity = 1.0 if rem > 0 else 0.0
            s = 0
            if adv > 0:
                s = 100000 + 5000 * adv - 10 * md
            else:
                s = 2000 * (-md) + 3 * od + (0 if rem > 6 else -2 * md)
            # Deterministic tie-break: prefer top-left-ish coordinates
            s += -(tx + 2 * ty)
            if best is None or s > best:
                best = s
                tx_best, ty_best = tx, ty
        return tx_best, ty_best

    tx, ty = best_target()

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer decreasing distance; if equal, prefer moves that also keep advantage over opponent.
        ndm = d
        ndo = cheb(nx, ny, tx, ty)  # same target
        # Advantage estimate at next position:
        adv_next = cheb(ox, oy, tx, ty) - ndm
        val = (-1000 * ndm) + (5000 * adv_next) + (-(nx + 2 * ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]