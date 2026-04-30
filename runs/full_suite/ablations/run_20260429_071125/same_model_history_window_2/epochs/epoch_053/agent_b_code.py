def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    def best_opp_dist(px, py, target):
        tx, ty = target
        d0 = cheb(px, py, tx, ty)
        best = d0
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                if d < best:
                    best = d
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Choose a target that we can reach well while the opponent struggles.
        # Deterministic: break ties by sorting score components implicitly via resource order.
        best_local = -10**9
        for tx, ty in resources:
            d_us = cheb(nx, ny, tx, ty)
            d_opp = best_opp_dist(ox, oy, (tx, ty))  # opponent best next move
            # Encourage getting closer than opponent; also prefer higher "future leverage" (smaller sum).
            val = (d_opp - d_us) * 10 - (d_us + d_opp)
            best_local = val if val > best_local else best_local

        # Penalize moving away from our current closest resource to avoid oscillation.
        closest = 10**9
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if d < closest:
                closest = d
        closest_after = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < closest_after:
                closest_after = d
        stick = (closest - closest_after) * 3

        total = best_local + stick
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]