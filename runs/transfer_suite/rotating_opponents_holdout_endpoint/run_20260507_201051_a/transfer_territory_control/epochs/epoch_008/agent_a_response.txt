def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def neigh_opp(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in opp_terr:
                return True
        return False

    def dist_to_targets(x, y, targets):
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best if best != 10**9 else 0

    opp_list = list(opp_terr) if opp_terr else [(ox, oy)]
    unq_list = list(unclaimed) if unclaimed else opp_list

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        score = 0

        if cell in opp_terr:
            score += 40  # flipping on entry
        if cell in unclaimed:
            score += 18
        if cell in self_terr:
            score += 6

        # Prefer advancing toward contested/unclaimed and into/near opponent territory.
        if cell in unclaimed or cell in opp_terr:
            score += 2

        if neigh_opp(nx, ny):
            score += 6

        score -= 0.8 * dist_to_targets(nx, ny, unq_list)
        score += 0.5 * dist_to_targets(nx, ny, opp_list)

        # Small bias to avoid getting stuck: prefer moves that change position unless equal.
        if (nx, ny) != (sx, sy):
            score += 0.2

        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]