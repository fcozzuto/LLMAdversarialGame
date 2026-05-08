def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    cap_r = observation.get("capture_radius", 0)
    self_role = (observation.get("self_role", "") or "").lower()

    obs = {(o[0], o[1]) for o in obstacles if isinstance(o, (list, tuple)) and len(o) >= 2}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    is_pursuer = ("pursuer" in self_role) or ("catch" in self_role) or ("chaser" in self_role)
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        d2 = dist2(nx, ny, px, py)
        captured = (cap_r == 0 and nx == px and ny == py) or (cap_r != 0 and d2 <= cap_r * cap_r)

        if captured:
            val = float("inf") if is_pursuer else -float("inf")
        else:
            # Deterministic wall-run / corridor bias for evader, direct chase bias for pursuer
            near_left = nx
            near_right = (w - 1 - nx)
            near_bottom = ny
            near_top = (h - 1 - ny)
            edge_dist = min(near_left, near_right, near_bottom, near_top)

            # Pursuer: prefer reducing distance and avoid getting "stuck" near edges when too close is worse
            if is_pursuer:
                # Larger score is better for us
                val = -d2 - 0.03 * edge_dist
                # Stronger preference for moving toward opponent's axis direction
                val -= 0.01 * (abs((nx - px)) + abs((ny - py)))
            else:
                # Evader: prefer increasing distance and hugging an edge aligned with where opponent is
                man = abs(nx - px) + abs(ny - py)
                # If opponent is more aligned vertically, hug left/right; else hug top/bottom
                vert_bias = 1.0 if abs(nx - px) > abs(ny - py) else 0.0
                edge_hug = (near_left if vert_bias > 0.5 else near_bottom)
                edge_hug2 = (near_right if vert_bias > 0.5 else near_top)
                hug = -min(edge_dist, min(edge_hug, edge_hug2))
                val = d2 + 0.08 * man + 0.02 * (-edge_dist) + 0.02 * hug

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
        else:
            better = val > best_val if is_pursuer else val > best_val
            # tie-break deterministically: prefer (0,0), then dx, then dy by fixed order in moves list
            if better:
                best_val = val
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]