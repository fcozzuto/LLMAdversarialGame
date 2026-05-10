def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2)

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def min_manh(a, bset):
        if not bset: return 10**9
        ax, ay = a
        best = 10**9
        for bx, by in bset:
            d = abs(bx - ax) + abs(by - ay)
            if d < best: best = d
        return best
    def adj_count(cell, s):
        x, y = cell
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) in s:
                c += 1
        return c

    frontier_opp = set()
    for ox, oy in opp_terr:
        for dx, dy in moves:
            nx, ny = ox + dx, oy + dy
            if inb(nx, ny) and ((nx, ny) in unclaimed or (nx, ny) in self_terr):
                frontier_opp.add((ox, oy))
                break

    target_type = "opp" if opp_terr else "unclaimed"
    best = None; bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        cell = (nx, ny)
        gain = 0
        if cell in self_terr:
            gain += 2
        if cell in unclaimed:
            gain += 6
        if cell in opp_terr:
            gain += 10  # strong flip incentive
        # Expand potential / control density
        gain += 2 * adj_count(cell, unclaimed)
        gain += 1 * adj_count(cell, self_terr)
        gain += 2 * adj_count(cell, opp_terr)
        # Prefer approaching the nearest relevant territory
        if target_type == "opp":
            dist = min_manh((nx, ny), frontier_opp or opp_terr)
            gain += max(0, 8 - dist)
        else:
            dist = min_manh((nx, ny), unclaimed)
            gain += max(0, 7 - dist)
        # Reduce immediate contention by avoiding stepping onto cells adjacent to many opp cells unless flipping them
        cont = adj_count(cell, opp_terr)
        if cell not in opp_terr:
            gain -= cont * 2

        # Deterministic tie-break: prefer staying if equal, else lexicographic dx,dy
        if gain > bestv or (gain == bestv and (best is None or (dx, dy) < best)):
            bestv = gain; best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]