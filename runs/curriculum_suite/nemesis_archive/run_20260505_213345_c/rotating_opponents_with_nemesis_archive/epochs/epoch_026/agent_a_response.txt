def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx + dy

    opp_row_bias = abs(oy - sy)  # larger => we are already far from sweep-row center
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Prefer resources in rows far from the opponent (anti sweep rows).
        row_far_bonus = 0
        row_far_bonus = abs(oy - ny) - opp_row_bias
        if row_far_bonus < 0:
            row_far_bonus *= 0.5

        # For each move, compute the best "steal advantage" target.
        best_gap = -10**9
        best_self_d = 10**9
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            gap = (opp_d - self_d)  # higher means we're closer than opponent
            # Add mild penalty for large travel; encourages earlier picks.
            gap -= 0.05 * self_d
            # Strongly prefer targets in rows far from opponent's row.
            gap += 0.12 * abs(oy - ry)
            if gap > best_gap or (gap == best_gap and self_d < best_self_d):
                best_gap = gap
                best_self_d = self_d

        # Tie-break: larger immediate row separation, then smaller distance, then deterministic move order.
        key = (best_gap + row_far_bonus, -best_self_d, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]