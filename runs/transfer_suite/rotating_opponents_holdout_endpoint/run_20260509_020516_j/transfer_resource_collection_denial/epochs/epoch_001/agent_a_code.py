def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # Choose nearest resource (deterministic tie-break by position)
    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            key = (d, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources visible: drift toward center
        tx, ty = (w // 2, h // 2)

    # Candidate moves: step toward target, or alternative minimizing distance
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            dist = abs(tx - nx) + abs(ty - ny)
            # Prefer moves that also reduce opponent distance to the same target resource
            opp_dist = abs(tx - (ox + dx)) + abs(ty - (oy + dy))
            key = (dist, opp_dist, abs(dx), abs(dy), nx, ny, dx, dy)
            candidates.append((key, (dx, dy)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return list(candidates[0][1])