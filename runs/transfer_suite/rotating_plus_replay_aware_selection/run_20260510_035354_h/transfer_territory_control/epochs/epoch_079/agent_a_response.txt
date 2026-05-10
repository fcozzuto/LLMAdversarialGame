def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    oppx, oppy = observation.get("opponent_position", (0, 0))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []

    def toset(lst):
        s = set()
        for p in lst:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    uset = toset(self_terr)
    oset = toset(opp_terr)
    ucell = toset(unclaimed)
    obset = toset(obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obset:
            continue

        # Heuristic value: prefer capturing unclaimed, then cracking opponent, else stay/advance.
        val = - (nx - ax) * (nx - ax) - (ny - ay) * (ny - ay)  # small preference for moving at most
        if (nx, ny) in ucell:
            val += 10000
        if (nx, ny) in oset:
            val += 8000
        if (nx, ny) in uset:
            val += 50  # avoid wandering into own territory less aggressively, but keep continuity

        # Also aim at the closest high-value target among unclaimed and adjacent-to-opponent cells.
        best_tgt = None
        best_d = 10**9
        if ucell:
            for tx, ty in ucell:
                d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                if d < best_d:
                    best_d = d
                    best_tgt = (tx, ty)
            if best_tgt is not None:
                val += max(0, 500 - best_d // 2)
        else:
            # If no unclaimed, seek adjacency to opponent territory to trigger counterclaim pressure.
            if oset:
                for tx, ty in oset:
                    for ax2, ay2 in ((tx-1, ty), (tx+1, ty), (tx, ty-1), (tx, ty+1), (tx-1, ty-1), (tx+1, ty+1), (tx-1, ty+1), (tx+1, ty-1)):
                        if inb(ax2, ay2) and (ax2, ay2) != (nx, ny) and (ax2, ay2) not in obset:
                            d = (ax2 - nx) * (ax2 - nx) + (ay2 - ny) * (ay2 - ny)
                            if d < best_d:
                                best_d = d
                                best_tgt = (ax2, ay2)
                if best_tgt is not None:
                    val += max(0, 400 - best_d // 2)

        # Prefer moving toward opponent overall when tied.
        val += -((nx - oppx) * (nx - oppx) + (ny - oppy) * (ny - oppy)) // 10
        cand.append((val, dx, dy, nx, ny))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy, _, _ = cand[0]
    return [int(dx), int(dy)]