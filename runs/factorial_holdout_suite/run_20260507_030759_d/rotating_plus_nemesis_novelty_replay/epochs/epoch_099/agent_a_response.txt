def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_corner_bias = (sx <= w // 2 and sy <= h // 2)
    best = None
    best_score = -10**18
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        adv = dO - dS  # positive means we can arrive no later than opponent
        # Prefer resources closer to "our" half/corner; if denier is faster, go to a denying-advantage target.
        corner = 1 if ((rx <= w // 2 and ry <= h // 2) == my_corner_bias) else 0
        score = adv * 10.0 + (-dS) + corner * 0.25
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dS2 = cheb(nx, ny, tx, ty)
                dO = cheb(ox, oy, tx, ty)
                adv2 = dO - dS2
                # Primary: minimize distance to target; Secondary: maximize arrival advantage; Tertiary: progress toward target (sum deltas).
                score = (-dS2) * 10.0 + adv2 + (-(abs(tx - nx) + abs(ty - ny))) * 0.001
                moves.append((score, dx, dy))
    moves.sort(reverse=True)
    return [int(moves[0][1]), int(moves[0][2])]