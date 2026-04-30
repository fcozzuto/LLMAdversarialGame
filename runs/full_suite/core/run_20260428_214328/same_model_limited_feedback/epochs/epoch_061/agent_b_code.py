def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neighbors_cell(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return (x, y)
        if (nx, ny) in obstacles:
            return (x, y)
        return (nx, ny)

    if resources:
        # New policy (vs last epoch): contest the resource the opponent is closest to (deny/interrupt),
        # but only switch targets if we can reach it much earlier.
        opp_best = min(resources, key=lambda r: dist((ox, oy), r))
        my_time = dist((sx, sy), opp_best)
        opp_time = dist((ox, oy), opp_best)
        # If we are not within striking distance, look for a safer alternative we can reach earlier.
        if my_time > opp_time + 1:
            target = min(resources, key=lambda r: dist((sx, sy), r) - 0.6 * dist((ox, oy), r))
        else:
            target = opp_best
    else:
        # No resources visible: move away from opponent to set up.
        target = None

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = neighbors_cell(sx, sy, dx, dy)
        if (nx, ny) == (sx, sy) and (dx, dy) != (0, 0):
            pass
        if target is None:
            tscore = dist((nx, ny), (ox, oy))
        else:
            tscore = -dist((nx, ny), target)  # closer is better
            # Deny: prefer increasing opponent distance from target
            opp_to_t = dist((ox, oy), target)
            opp_to_next = dist((ox, oy), target)  # opponent position fixed this turn
            tscore += 0.10 * opp_to_t
            # Safety / interference: avoid walking into the opponent
            tscore += 0.08 * dist((nx, ny), (ox, oy))
            # Discourage staying put when resources exist
            if (dx, dy) == (0, 0):
                tscore -= 0.03
        # Small tie-breaker: deterministic preference order encoded by score only
        # Slightly favor moving closer to target in diagonal direction by lexicographic bias
        bias = -0.001 * (dx * 3 + dy)
        score = tscore + bias

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move