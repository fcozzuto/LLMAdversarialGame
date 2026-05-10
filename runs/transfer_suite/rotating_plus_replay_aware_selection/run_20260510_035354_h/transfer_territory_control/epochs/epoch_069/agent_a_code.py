def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    targets = []
    for key in ("resources", "unclaimed_cells"):
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                targets.append((p[0], p[1]))
        if targets:
            break

    self_cells = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            self_cells.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in self_cells:
            sc += 3
        d_opp = man(nx, ny, ox, oy)
        sc -= 2 * d_opp
        if targets:
            d_t = min(man(nx, ny, tx, ty) for (tx, ty) in targets)
            sc += 6 - d_t
            for (tx, ty) in targets:
                if man(nx, ny, tx, ty) == 1:
                    sc += 4
                    break
        else:
            sc += 4 - d_opp
        if best is None or sc > best_sc or (sc == best_sc and (dx, dy) < best):
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]