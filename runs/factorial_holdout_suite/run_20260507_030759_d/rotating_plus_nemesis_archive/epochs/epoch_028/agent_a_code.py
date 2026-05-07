def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    w, h = int(observation.get("grid_width", 8)), int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = [(int(r[0]), int(r[1])) for r in resources]
    res.sort()
    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        my_pos = (nx, ny)

        # Pick the most favorable resource for us after this move.
        best_for_move = -10**18
        best_tie = None
        for r in res:
            my_d = md(my_pos, r)
            op_d = md((ox, oy), r)
            # Positive is good (we are closer); encourage being first, penalize delay.
            ahead = op_d - my_d
            val = ahead * 10 - my_d
            # Small deterministic tie preference toward "lower" resource id
            tie = (r[0], r[1], my_d, op_d)
            if val > best_for_move or (val == best_for_move and tie < best_tie):
                best_for_move = val
                best_tie = tie

        # If no move increased "ahead" meaningfully, still reduce own distance to nearest resource.
        if best_for_move < -10**17:
            best_for_move = -min(md(my_pos, r) for r in res)

        if best_for_move > best_val or (best_for_move == best_val and (dx, dy) < best_move):
            best_val = best_for_move
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]