def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_role = str(observation.get("self_role", ""))
    opponent_role = str(observation.get("opponent_role", ""))
    pursuer = ("pursuer" in self_role.lower()) or ("pursuer" in opponent_role.lower() and "evader" in self_role.lower())
    # If roles ambiguous, default to pursuer-like behavior.
    if "evader" in self_role.lower() and "pursuer" in opponent_role.lower():
        pursuer = False

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18 if pursuer else -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        d = abs(ox - nx) + abs(oy - ny)
        # Corner shaping: pursuer wants opponent-driven corner pressure; evader wants self survival corner distance.
        if pursuer:
            far_c = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            corner_pressure = abs(far_c[0] - nx) + abs(far_c[1] - ny)
            # Prefer reducing distance primarily, then reduce corner_pressure to prevent opponent from escaping to that far corner.
            val = (-d * 100) - corner_pressure
        else:
            far_from_opp = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            escape_dir = abs(far_from_opp[0] - nx) + abs(far_from_opp[1] - ny)
            # Prefer increasing distance and moving toward the corner that is farthest from opponent.
            val = (d * 100) + escape_dir

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]