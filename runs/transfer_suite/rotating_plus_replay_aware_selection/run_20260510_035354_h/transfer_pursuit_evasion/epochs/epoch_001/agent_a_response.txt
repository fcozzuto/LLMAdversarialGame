def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer_like = ("purs" in self_role) or (self_role == "pursuer") or ("purs" in opp_role and "evad" in self_role)
    # Candidate moves (including stay), deterministic order
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cx, cy = (w-1)/2.0, (h-1)/2.0

    def clamp(x, a, b):
        return a if x < a else b if x > b else x

    def valid(nx, ny):
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist2 = (nx - ox)*(nx - ox) + (ny - oy)*(ny - oy)
        # center bias
        center2 = (nx - cx)*(nx - cx) + (ny - cy)*(ny - cy)
        # Obstacle/edge avoidance: prefer not-too-close to corners for evader
        edge_pen = min(nx, w-1-nx) + min(ny, h-1-ny)

        if pursuer_like:
            # minimize distance; slight center bias to avoid corner traps
            val = dist2 * 1000.0 + center2 * 0.01 + (-edge_pen) * 0.1
            better = best_val is None or val < best_val
        else:
            # maximize distance; prefer staying closer to center; avoid edges/corners
            val = -dist2 * 1000.0 + center2 * 0.02 + edge_pen * 0.5
            better = best_val is None or val > best_val

        if better:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]