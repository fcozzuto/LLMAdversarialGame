def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def edge_dist(x, y):
        a = x if x < w - 1 - x else w - 1 - x
        b = y if y < h - 1 - y else h - 1 - y
        return a if a < b else b

    def best_resource_from(x, y):
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            # Prefer closer resources; tie-break deterministically by coordinates.
            key = (d, abs(rx - ox) + abs(ry - oy), rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry, d)
        return best[1], best[2], best[3]

    # If no resources, retreat toward interior while not giving chase lines.
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = 10 * edge_dist(nx, ny) + cheb(nx, ny, ox, oy) - 0.01 * (dx * dx + dy * dy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Greedy: move to maximize progress to the best remaining resource, with mild opponent-avoidance and interior bias.
    we_edge = edge_dist(sx, sy)
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        rx, ry, d = best_resource_from(nx, ny)
        if rx is None:
            continue

        # Penalize getting too close to opponent (safe_collector tends to stick to efficient paths).
        opp_close = cheb(nx, ny, ox, oy)
        # Encourage interior capture lane when we are leading on resources.
        interior_bonus = edge_dist(nx, ny) - we_edge

        # If adjacent to a resource, prioritize strongly.
        score = 1000 * (1 if d == 0 else 0) + 200 * (1 if d == 1 else 0)
        score += 50 / (1 + d)  # closer is better
        score += 0.8 * interior_bonus
        score += 0.15 * opp_close  # stay away

        # Also consider whether this step blocks the opponent by moving closer to the same resource.
        opp_rx, opp_ry, opp_d = best_resource_from(ox, oy)
        if opp_rx is not None:
            score -= 0.2 * max(0, (opp_d - d))  # reduce if we would enable their approach

        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]