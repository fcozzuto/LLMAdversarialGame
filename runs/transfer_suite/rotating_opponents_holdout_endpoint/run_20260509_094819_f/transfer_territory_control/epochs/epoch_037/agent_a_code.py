def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    blocked = lambda x, y: (x, y) in obstacles

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    resources = observation.get("resources") or []
    best_target = None

    if resources:
        best_target = min(
            [(int(p[0]), int(p[1])) for p in resources if p and inb(int(p[0]), int(p[1])) and not blocked(int(p[0]), int(p[1]))],
            key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]),
            default=None,
        )
    if best_target is None:
        # Prefer expanding from our frontier: cells near our territory that are unclaimed or enemy
        frontier = set()
        for x, y in selfT:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and not blocked(nx, ny) and (nx, ny) not in selfT:
                        frontier.add((nx, ny))
        cand = [c for c in frontier if c in uncla or c in oppT]
        if not cand:
            cand = [c for c in uncla if inb(c[0], c[1]) and not blocked(c[0], c[1])]
        if cand:
            # Deterministic tie-break on coordinates
            best_target = min(cand, key=lambda t: (max(abs(t[0]-sx), abs(t[1]-sy)), t[0], t[1]))

    if best_target is None:
        best_target = (0, 0)

    tx, ty = best_target

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def cheb(x, y): return max(abs(x - sx), abs(y - sy))
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        # Base: move closer to target
        score = -cheb(nx, ny) * 2

        # Prefer claiming unclaimed; if enemy, prefer only when we can get there first
        if (nx, ny) in uncla:
            score += 18
        elif (nx, ny) in oppT:
            score += 26
            my_d = dist(nx, ny, ox, oy)
            opp_d = dist(ox, oy, nx, ny)
            # Since flipping is on entry, discourage suicide into enemy-controlled area when opponent is adjacent
            if my_d <= 2:
                score -= 14

        # Avoid moving into cells that are already ours (slow expansion) unless needed
        if (nx, ny) in selfT:
            score -= 3

        # Mild anti-collision: keep distance from opponent
        score -= max(0, 6 - (abs(nx - ox) + abs(ny - oy)))

        # Deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]