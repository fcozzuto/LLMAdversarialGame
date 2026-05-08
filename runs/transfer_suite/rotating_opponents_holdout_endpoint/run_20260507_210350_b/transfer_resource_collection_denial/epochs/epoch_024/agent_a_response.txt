def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1, 0) if (sx + sy) % 2 == 0 else (0, h - 1)
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Pick the resource that maximizes "expected advantage" from this step.
        move_score = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)

            # Primary: being strictly earlier; Secondary: how much earlier;
            # Tertiary: closer to the resource (reduces time wasted).
            earlier = (do - ds)
            score = 0
            if ds < do:
                score += 100000 + earlier * 100
            else:
                score += earlier * 30  # still try contested resources that deny us less

            score += -ds  # prefer shorter paths when contest is similar
            # Small tie-breaking: prefer resources that are farther from opponent when not winning outright.
            if ds >= do:
                score += -man(ox, oy, rx, ry) * 0.5

            if score > move_score:
                move_score = score

        # If two moves have similar move_score, prefer the one that increases distance from opponent (denial pressure).
        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)
        elif move_score == best_score:
            if man(nx, ny, ox, oy) > man(sx, sy, ox, oy):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]