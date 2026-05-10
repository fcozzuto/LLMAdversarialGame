def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    my_set = set((p[0], p[1]) for p in (observation.get("self_territory") or []))
    opp_set = set((p[0], p[1]) for p in (observation.get("opponent_territory") or []))
    un_set = set((p[0], p[1]) for p in (observation.get("unclaimed_cells") or []))
    myc = observation.get("self_territory_count", len(my_set))
    opc = observation.get("opponent_territory_count", len(opp_set))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(a, b, c, d): 
        dx = abs(a - c); dy = abs(b - d)
        return dx if dx > dy else dy
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    # If behind: strike near opponent frontier (unclaimed adjacent to opp), else edge expansion.
    behind = myc < opc
    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0

    opp_front = []
    if behind and un_set:
        for (x, y) in un_set:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx or dy:
                        if (x + dx, y + dy) in opp_set:
                            opp_front.append((x, y))
                            dx = dy = 2
                            break

    if behind and opp_front:
        # Closest frontier point, with slight bias to avoid center (since opponent owns center).
        tx, ty = min(opp_front, key=lambda p: (man(sx, sy, p[0], p[1]), -((p[0]-centerx)**2 + (p[1]-centery)**2)))
    else:
        # Expand to farthest-from-center unclaimed; if none, expand to farthest-from-center among all cells not blocked (prefer unclaimed).
        candidates = list(un_set) if un_set else []
        if not candidates:
            candidates = [(x, y) for x in range(w) for y in range(h) if (x, y) not in obstacles and (x, y) not in my_set and (x, y) not in opp_set]
            if not candidates:
                candidates = list(un_set) if un_set else [(sx, sy)]
        tx, ty = max(candidates, key=lambda p: (((p[0]-centerx)**2 + (p[1]-centery)**2), -man(sx, sy, p[0], p[1])))

    # Choose move that gets us closest to target; tie-break by threatening opponent territory if adjacent.
    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        target_dist = cheb(nx, ny, tx, ty)
        threaten = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax or ay:
                    if (nx + ax, ny + ay) in opp_set:
                        threaten = 1
                        ax = ay = 2
                        break
        # Prefer direct adjacency to opponent; otherwise shortest distance; also keep inside bounds already ensured.
        key = (0 if threaten else 1, target_dist, man(nx, ny, tx, ty), abs(nx - tx) + abs(ny - ty))
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]