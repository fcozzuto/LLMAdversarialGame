def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    unclaimed = observation.get("unclaimed_cells") or []
    self_ter = set((c[0], c[1]) for c in (observation.get("self_territory") or []))
    opp_ter = set((c[0], c[1]) for c in (observation.get("opponent_territory") or []))
    if not unclaimed:
        unclaimed = [[x, y] for x in range(w) for y in range(h) if (x, y) not in self_ter and (x, y) not in opp_ter]

    best_cell = None
    best_score = None

    for cell in unclaimed:
        tx, ty = int(cell[0]), int(cell[1])
        if not inb(tx, ty) or (tx, ty) in obstacles:
            continue
        d_self = abs(tx - sx) + abs(ty - sy)
        d_opp = abs(tx - ox) + abs(ty - oy)
        if (tx, ty) in self_ter:
            gain = 1000
        elif (tx, ty) in opp_ter:
            gain = -1000
        else:
            gain = 0
        # Prefer cells we can reach earlier; small preference to being closer to our current position.
        score = gain + (d_opp - d_self) * 10 - d_self
        # Deterministic tie-break
        if best_score is None or score > best_score or (score == best_score and (tx, ty) < (best_cell[0], best_cell[1])):
            best_score = score
            best_cell = (tx, ty)

    if best_cell is None:
        return [0, 0]

    tx, ty = best_cell
    # Greedy move: minimize distance to target; avoid obstacles; deterministic tie-break.
    best_move = (0, 0)
    best_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) < best_move):
            best_dist = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]