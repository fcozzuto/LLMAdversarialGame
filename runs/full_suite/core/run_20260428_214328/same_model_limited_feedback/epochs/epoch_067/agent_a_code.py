def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    remaining = observation.get("remaining_resource_count", len(resources))

    # Move deltas in deterministic order (prefer diagonals, then straight, then stay)
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def best_move(targets, avoid_opponent=False):
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Chebyshev distance appropriate for 8-dir movement
            if targets:
                d = min(max(abs(nx - tx), abs(ny - ty)) for tx, ty in targets)
            else:
                # fallback to center
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                d = max(abs(nx - cx), abs(ny - cy))
            # Prefer closer and (slightly) away from opponent if requested
            opp_pen = 0
            if avoid_opponent:
                opp_pen = -0.01 * (max(abs(nx - ox), abs(ny - oy)))
            score = (d, opp_pen, abs(dx), abs(dy), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # If resources exist: head to closest reachable resource, and sometimes avoid opponent
    if remaining > 0 and resources:
        # Determine "threat" by whether opponent is closer to the nearest resource
        my_near = min(resources, key=lambda p: max(abs(sx - p[0]), abs(sy - p[1])))
        opp_near_dist = min(max(abs(ox - rx), abs(oy - ry)) for rx, ry in resources)
        my_near_dist = max(abs(sx - my_near[0]), abs(sy - my_near[1]))
        avoid = opp_near_dist <= my_near_dist
        return best_move(resources, avoid_opponent=avoid)

    # No resources: move toward opponent's side or center depending on stage
    center_target = [(w - 1) // 2, (h - 1) // 2]
    # Deterministic: if tied to "resources gone", go toward opponent
    if remaining <= 0:
        return best_move([(ox, oy)], avoid_opponent=False)
    return best_move([tuple(center_target)], avoid_opponent=False)