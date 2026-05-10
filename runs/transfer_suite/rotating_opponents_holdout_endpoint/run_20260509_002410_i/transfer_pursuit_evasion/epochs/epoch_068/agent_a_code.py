def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    is_pursuer = (observation.get("self_role", "pursuer") == "pursuer")

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def edge_score(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)  # larger = more central

    best_move = [0, 0]
    best_key = None

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic preference ordering for ties:
    # pursuer: toward movement (dx,dy) closer to direction; evader: away and toward edges.
    dirx = 0 if ox == sx else (1 if ox > sx else -1)
    diry = 0 if oy == sy else (1 if oy > sy else -1)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d = dist2(nx, ny, ox, oy)

        # Additional look: estimate how good this move is relative to my alternatives.
        # For pursuer, prefer moves that improve distance more than staying.
        # For evader, prefer moves that worsen distance more than staying.
        stay_d = dist2(sx, sy, ox, oy)
        delta = d - stay_d

        # Secondary tie-breakers:
        # pursuer -> avoid centralization, and prefer to move at least one step when possible
        # evader -> prefer boundaries (harder to corner), and prefer larger distance
        move_mag = abs(dx) + abs(dy)
        if is_pursuer:
            primary = (d, -move_mag, edge_score(nx, ny))
            # Make sure we never choose a worse-than-stay move when any equal/near exists.
            key = (primary[0], primary[1], primary[2], delta)
        else:
            # edge preference: smaller edge_score => more toward edges
            primary = (-d, move_mag, edge_score(nx, ny))
            key = (primary[0], primary[1], primary[2], -delta)

        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    # If all moves blocked (should be rare), stay still deterministically.
    return [int(best_move[0]), int(best_move[1])]