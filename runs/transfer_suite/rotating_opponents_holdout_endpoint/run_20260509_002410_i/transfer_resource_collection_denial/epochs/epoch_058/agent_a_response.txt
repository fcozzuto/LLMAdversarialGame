def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if r and len(r) >= 2:
            rx = int(r[0]); ry = int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                targets.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not targets:
        return [0, 0]

    # If resources are on current cell, prefer staying (collect) unless invalid (shouldn't be).
    if (sx, sy) in targets:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_score = 0.0
        nearest_gap = 10**9
        for rx, ry in targets:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - md  # positive means we are closer or equal
            if gap >= 0:
                my_score += 5.0 / (md + 1) + 0.5 * gap
            else:
                # avoid moving that grants opponent strong access
                my_score += -1.5 / (abs(gap) + 1)
            if md < nearest_gap:
                nearest_gap = md

        # small tie-break: move that is closer to some resource, and farther from opponent slightly
        my_score += 0.05 * (1.0 / (nearest_gap + 1))
        my_score += 0.02 * cheb(nx, ny, ox, oy)

        if my_score > best_score:
            best_score = my_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]