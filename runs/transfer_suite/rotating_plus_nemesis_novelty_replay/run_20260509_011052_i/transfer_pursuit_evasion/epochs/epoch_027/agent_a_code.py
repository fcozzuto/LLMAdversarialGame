def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = (observation.get("self_role") or "").lower()
    i_am_evader = "evader" in self_role

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def dist_to_corner(x, y, pick_far):
        # Manhattan to farthest/nearest corner
        if pick_far:
            return max(abs(x - cx) + abs(y - cy) for cx, cy in corners)
        return min(abs(x - cx) + abs(y - cy) for cx, cy in corners)

    def king_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def obstacle_repulsion(x, y):
        # Strongly penalize being adjacent or on (we already filter moves)
        r = 0
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                r += 100000
            elif d == 1:
                r += 25
            elif d == 2:
                r += 8
            elif d == 3:
                r += 3
        return r

    best_move = (0, 0)
    if i_am_evader:
        best_score = -10**18
        pick_far = True
        toward_corner_weight = 1.1
    else:
        best_score = -10**18
        pick_far = False
        toward_corner_weight = 0.9

    # Deterministic tie-break order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d = king_dist(nx, ny, ox, oy)
        rep = obstacle_repulsion(nx, ny)

        # Bias: evader wants farthest corner; pursuer wants nearest corner away from opponent using that same corner target.
        corner_bias = dist_to_corner(nx, ny, pick_far)
        # Wall-run counter: prefer steps that increase distance *most*, then keep moving along a consistent direction.
        score = d
        if not i_am_evader:
            score = -d

        # Add corner and obstacle considerations
        if i_am_evader:
            score += toward_corner_weight * corner_bias
            score -= rep
            # Extra: avoid drifting toward opponent's side by discouraging reducing Manhattan to nearest corner of opponent side
            score += 0.15 * (abs(nx - ox) + abs(ny - oy))
        else:
            score += (-toward_corner_weight * corner_bias)  # nearest corner -> smaller bias
            score -= 0.7 * rep

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves blocked (unlikely), stay put
    return [int(best_move[0]), int(best_move[1])]