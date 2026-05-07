def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Candidate next steps (deterministic order)
    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose best resource to target from (nx, ny) using relative distance.
        # Primary: maximize (opp_dist - self_dist). Secondary: minimize self_dist.
        best_t = None
        best_pair = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            pair = (od - sd, -sd, rx, ry)  # lexicographic
            if best_pair is None or pair > best_pair:
                best_pair = pair
                best_t = (rx, ry)

        if best_t is None:
            continue

        # Tie-break with actual move preference closer to target
        rx, ry = best_t
        sd_now = dist(nx, ny, rx, ry)
        val = (best_pair[0], best_pair[1], -sd_now, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]