def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    opp = (ox, oy)

    # Evaluate best "contested" resource after making one move; prefer resources we reach no later than opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_pos = (nx, ny)

        move_score = 0
        for (rx, ry) in resources:
            cell = (rx, ry)
            d_self = man(self_pos, cell)
            d_opp = man(opp, cell)

            # If we can take it this turn (or at all before/at opponent), make it dominant.
            if d_self == 0:
                win_take = 10**9
            else:
                win_take = 0

            # Contention advantage: earlier is better; ties still good to counter deniers.
            adv = d_opp - d_self  # positive if we are sooner
            if adv >= 0:
                # Weight by closeness and by how strongly we beat/deny opponent.
                # Deterministic tie-break via coordinates.
                win = 1000000 * adv + (2000 - d_self * 5) - (rx + ry)
                move_score = max(move_score, win + win_take)
            else:
                # If opponent likely grabs it before us, consider denial only if very close.
                if d_self <= 2:
                    deny = -200000 + (2 - d_self) * 1000 - (rx + ry)
                    move_score = max(move_score, deny)

        # Small preference for staying mobile when scores are similar.
        mobility = -man(self_pos, opp)
        total = move_score * 10 + mobility
        # Deterministic tie-break: lexicographic on (dx, dy).
        if total > best_score or (total == best_score and (dx, dy) < best_move):
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]