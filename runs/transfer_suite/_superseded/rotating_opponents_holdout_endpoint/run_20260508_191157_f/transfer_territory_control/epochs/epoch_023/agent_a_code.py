def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            obstacles.add((p[0], p[1]))

    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []) if p and len(p) == 2)
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []) if p and len(p) == 2)
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or []) if p and len(p) == 2]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    targets = []
    for c in unclaimed:
        if c not in self_terr:
            targets.append(c)
    if not targets:
        for c in opp_terr:
            targets.append(c)

    # If unclaimed exists, prefer cells adjacent to opponent territory to counterclaim quickly
    if unclaimed and opp_terr:
        best_adj = None
        for tx, ty in unclaimed:
            if (tx, ty) in self_terr:
                continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = tx + dx, ty + dy
                    if (nx, ny) in opp_terr:
                        score = manh(sx, sy, tx, ty) - 0.01 * manh(ox, oy, tx, ty)
                        if best_adj is None or score < best_adj[0]:
                            best_adj = (score, (tx, ty))
                        break
                if best_adj is not None and best_adj[0] == score:
                    break
        if best_adj is not None:
            targets = [best_adj[1]]

    # Also bias towards crossing the widest gap between opponent and us
    if not targets:
        targets = [(w - 1, h - 1), (0, h - 1), (w - 1, 0), (0, 0)]

    tx, ty = min(targets, key=lambda c: (manh(sx, sy, c[0], c[1]), -manh(ox, oy, c[0], c[1])))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, manh(nx, ny, tx, ty), 0))
    moves.append((0, 0, manh(sx, sy, tx, ty), 1))

    # Tie-break deterministically by direction ordering
    order = {(1, 0): 0, (0, 1): 1, (1, 1): 2, (-1, 0): 3, (0, -1): 4, (-1, -1): 5, (1, -1): 6, (-1, 1): 7, (0, 0): 8}
    best = min(moves, key=lambda m: (m[2], order[(m[0], m[1])]))
    return [int(best[0]), int(best[1])]