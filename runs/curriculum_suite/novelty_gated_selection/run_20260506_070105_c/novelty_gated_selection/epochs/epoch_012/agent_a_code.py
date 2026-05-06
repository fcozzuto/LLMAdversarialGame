def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = (None, -10**18, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Anti-sweep heuristic: opponent likely concentrates on its current row.
        # Prefer resources on rows away from the opponent, and only contest when advantageous.
        cell_my = man(nx, ny, ox, oy)
        best_res_val = -10**18
        best_my_d = 10**9

        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            row_diff = abs(ry - oy)

            # Strong advantage term; de-emphasize resources on opponent's row (potential sweep track).
            val = (opp_d - my_d) * 5.0
            val += (row_diff * 1.2)  # go to different rows
            val -= my_d * 0.35       # still make progress
            # If we are within striking distance, slightly favor contesting that specific resource.
            val += max(0.0, (10 - (my_d + opp_d)) * 0.05)

            if val > best_res_val or (val == best_res_val and my_d < best_my_d):
                best_res_val = val
                best_my_d = my_d

        # Prefer moves that reduce our best distance; small tie-break away from getting stuck.
        score = best_res_val - best_my_d * 0.25 - cell_my * 0.02
        if score > best[1] or (score == best[1] and best_my_d < best[2]):
            best = ((dx, dy), score, best_my_d)

    return [best[0][0], best[0][1]]