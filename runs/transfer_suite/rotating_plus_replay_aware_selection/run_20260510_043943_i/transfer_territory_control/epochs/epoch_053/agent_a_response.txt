def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    self_cells = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_cells = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # Target: best unclaimed; if none, best frontier (adjacent to unclaimed); if none, approach opponent.
    if unclaimed:
        targets = list(unclaimed)
        targets.sort(key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
        tx, ty = targets[0]
    else:
        frontier = set()
        for cx, cy in self_cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                        if (nx, ny) not in obstacles:
                            frontier.add((nx, ny))
        if frontier:
            ft = list(frontier)
            ft.sort(key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
            tx, ty = ft[0]
        else:
            tx, ty = ox, oy

    # Evaluate moves: closer to target, prefer stealing/expanding into higher-value cells, avoid opponent proximity if it risks loss.
    best = None
    for dx, dy, nx, ny in legal:
        d = abs(nx - tx) + abs(ny - ty)
        md = abs(nx - ox) + abs(ny - oy)
        steal = 1 if (nx, ny) in opp_cells else 0
        grab_unclaimed = 1 if (nx, ny) in unclaimed else 0
        stay_self = 1 if (nx, ny) in self_cells else 0

        # Deterministic score (maximize): primary minimize d via negative, then prefer grabbing/stealing.
        val = (-d * 10) + (steal * 18) + (grab_unclaimed * 8) + (stay_self * 2) - (md * 0.5)
        key = (val, -d, -steal, -grab_unclaimed, nx, ny)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]