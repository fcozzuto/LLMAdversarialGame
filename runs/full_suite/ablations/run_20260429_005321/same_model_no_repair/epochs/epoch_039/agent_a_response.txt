def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        # deterministic retreat/approach toward opponent
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        return [dx, dy]

    center_x = (gw - 1) // 2
    center_y = (gh - 1) // 2

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Evaluate best resource to pursue from next position using opponent-relative advantage.
        cur_best = -10**18
        for rx, ry in resources:
            my_d = king_dist(nx, ny, rx, ry)
            opp_d = king_dist(ox, oy, rx, ry)
            # Want to minimize my_d, and maximize advantage where I'm closer than opponent.
            # Also slightly prefer nearer resources overall and avoid drifting to edges.
            edge_pen = abs(nx - center_x) + abs(ny - center_y)
            advantage = opp_d - my_d  # positive means I'm closer
            score = (-my_d) + (0.75 * advantage) - (0.03 * edge_pen)
            if score > cur_best:
                cur_best = score

        # If multiple moves tie, deterministically break by preferring lower my_dist to the best resource set.
        if cur_best > best_score:
            best_score = cur_best
            best_move = (dx, dy)
        elif cur_best == best_score:
            # tie-break: prefer move that reduces distance to the nearest resource from next
            def nearest_from(x, y):
                md = 10**9
                for rx, ry in resources:
                    d = king_dist(x, y, rx, ry)
                    if d < md:
                        md = d
                return md
            if nearest_from(nx, ny) < nearest_from(sx + best_move[0], sy + best_move[1]):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]