def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    rem = observation["remaining_resource_count"]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = None

    # If no resources, head toward opponent to deny space (deterministic)
    if not resources:
        tx, ty = ox, oy
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -cheb(nx, ny, tx, ty)
                if best_val is None or val > best_val:
                    best_val = val
                    best = [dx, dy]
        return best if best is not None else [0, 0]

    # Heuristic: prioritize resources where we are relatively closer than opponent.
    # If very few resources remain, switch to nearest-to-us to secure.
    secure = rem <= 3

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if secure:
            # Go for the closest resource.
            val = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                v = -d
                if val is None or v > val:
                    val = v
        else:
            # For each candidate, take the best resource advantage; also avoid letting opponent have a closer lane.
            val = None
            for rx, ry in resources:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer; penalize if opponent is much closer.
                # Slightly prefer smaller our_d to keep progress.
                v = (opp_d - our_d) * 10 - our_d
                if val is None or v > val:
                    val = v
            # Extra tie-break: keep distance from opponent unless there is clear advantage.
            # (Avoid drifting into opponent's path when scores are tied.)
            val -= cheb(nx, ny, ox, oy) * 0.01

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]