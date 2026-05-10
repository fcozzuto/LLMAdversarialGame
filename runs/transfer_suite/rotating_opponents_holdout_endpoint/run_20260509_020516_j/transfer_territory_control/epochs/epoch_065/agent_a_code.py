def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))
    unclaimed = set()
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                unclaimed.add((x, y))
    my_t = set()
    for p in observation.get("self_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                my_t.add((x, y))
    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                opp_t.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    oppx, oppy = int(op[0]), int(op[1])
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        if cell in opp_t:
            val = 6.0
        elif cell in unclaimed:
            val = 3.0
        elif cell in my_t:
            val = 1.0
        else:
            val = 1.2

        # Prefer reducing distance to opponent and reaching unclaimed/opp cells
        md = abs(nx - oppx) + abs(ny - oppy)
        val += -0.02 * md

        # Prefer moving toward nearest "good" cell if available
        if unclaimed:
            # cheap approximate: aim to edge toward cells' median-ish by direction
            if unclaimed:
                # deterministically pick a target direction based on min manhattan to avoid sorting costs
                tx, ty = None, None
                bestd = 10**9
                for x, y in unclaimed:
                    d = abs(x - sx) + abs(y - sy)
                    if d < bestd:
                        bestd = d
                        tx, ty = x, y
                val += 0.03 * (-(abs(nx - tx) + abs(ny - ty)))
        elif opp_t:
            val += 0.02 * (-(min(abs(nx - x) + abs(ny - y) for x, y in opp_t)))

        # Small preference for not oscillating out of bounds/obstacles and for staying if equal
        if (dx, dy) == (0, 0):
            val -= 0.01

        if val > best_val or (val == best_val and (dx, dy) == (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]