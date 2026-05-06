def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_resource_for(posx, posy):
        br = resources[0]
        bd = md(posx, posy, br[0], br[1])
        for rx, ry in resources[1:]:
            d = md(posx, posy, rx, ry)
            if d < bd:
                bd = d
                br = (rx, ry)
        return br[0], br[1], bd

    tx, ty, d_op_target = best_resource_for(ox, oy)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_score = 10**18
    best_move = (0, 0)
    best_center = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        # Own progress: nearest resource
        d_our_nearest = 10**9
        for rx, ry in resources:
            d = md(nx, ny, rx, ry)
            if d < d_our_nearest:
                d_our_nearest = d

        # Denial: reach the resource currently closest to opponent
        d_our_target = md(nx, ny, tx, ty)

        # Edge/patrol handling: if opponent is near an edge, prioritize contesting its closest target
        on_edge = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)
        edge_bonus = -2.0 if on_edge else 0.0  # reduce score when opponent likely patrolling edges

        # Lower is better. Reward getting closer to target than opponent (compared to current opponent distance).
        score = (d_our_target - 0.9 * d_op_target) + 0.55 * d_our_nearest + edge_bonus

        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        if score < best_score or (score == best_score and center > best_center):
            best_score = score
            best_move = (dx, dy)
            best_center = center

    return [int(best_move[0]), int(best_move[1])]