def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def moves_list():
        return [(-1, -1), (0, -1), (1, -1),
                (-1, 0), (0, 0), (1, 0),
                (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set((r[0], r[1]) for r in resources)
    opp_next_moves = set()
    for dx, dy in moves_list():
        px, py = ox + dx, oy + dy
        if inb(px, py) and (px, py) not in obstacles:
            opp_next_moves.add((px, py))

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves_list():
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        if (nx, ny) in res_set:
            return [dx if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles else 0, dy if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles else 0]

        score = 0
        # Immediate safety: avoid moving into opponent's immediate capture neighborhood.
        if cheb(nx, ny, ox, oy) <= 1:
            score -= 40

        # Evaluate targets: prefer resources we can approach faster than opponent
        # and that opponent cannot take next turn from any of its legal next squares.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Can opponent capture this resource next turn (from its legal move set)?
            capt_next = False
            for px, py in opp_next_moves:
                if cheb(px, py, rx, ry) <= 0:
                    capt_next = True
                    break

            # Better targets: we are closer or we will become closer than opponent.
            score += (opd - myd) * 12

            if (rx, ry) in opp_next_moves:
                score -= 180  # opponent can land on that resource next turn
            if capt_next:
                score -= 160

            # Mild preference for nearer resources
            score -= myd * 3

        # Tie-break deterministically: prefer moves that increase distance from opponent if scores equal
        score += -cheb(nx, ny, ox, oy)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break
            if cheb(nx, ny, ox, oy) > cheb(sx + best_move[0], sy + best_move[1], ox, oy):
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]