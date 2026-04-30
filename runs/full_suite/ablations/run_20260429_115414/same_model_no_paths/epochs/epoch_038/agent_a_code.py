def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx = cy = 0
    if resources:
        for rx, ry in resources:
            cx += rx
            cy += ry
        cx /= len(resources)
        cy /= len(resources)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if resources:
            # Best "steal potential": how much closer we are than opponent to some remaining resource
            best_adv = -10**18
            best_self_d = 10**9
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                adv = od - sd
                if adv > best_adv or (adv == best_adv and sd < best_self_d):
                    best_adv = adv
                    best_self_d = sd
            # Small bias toward overall centroid (keeps policy different from pure nearest-resource)
            center_bias = -cheb(nx, ny, int(cx + 0.5), int(cy + 0.5))
            score = best_adv * 1000 - best_self_d + center_bias
        else:
            # No visible resources: drift toward opponent mirror pressure (toward their position)
            score = -cheb(nx, ny, ox, oy)

        # Deterministic tie-break (prefer staying put)
        score -= (dx != 0 or dy != 0) * 0.01
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]