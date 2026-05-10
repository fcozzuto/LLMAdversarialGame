def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    dirs8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def adj4(x, y):
        return [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

    def manhattan_to_target(x, y, targets):
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best

    # Targets: prioritize unclaimed; otherwise push near opponent.
    if unclaimed:
        targets = list(unclaimed)
    else:
        targets = list(opp_terr) if opp_terr else [(ox, oy)]

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**12
        else:
            # Immediate territory effect (flipping on entry enabled)
            in_opp = (nx, ny) in opp_terr
            in_self = (nx, ny) in self_terr
            in_un = (nx, ny) in unclaimed

            a_self = sum(1 for p in adj4(nx, ny) if p in self_terr)
            a_opp = sum(1 for p in adj4(nx, ny) if p in opp_terr)

            # Distance heuristics to control "front"
            d_opp = abs(nx - ox) + abs(ny - oy)
            d_target = manhattan_to_target(nx, ny, targets)

            # Score shaping: claim/flip > expand > avoid being surrounded
            val = 0
            if in_self:
                val += 0
            if in_un:
                val += 6
            if in_opp:
                val += 14
            # Prefer moves that build edges (more own adjacency, less opponent adjacency)
            val += 3.0 * a_self
            val -= 2.6 * a_opp
            # Keep pressure without over-committing into opponent blobs
            val -= 0.08 * d_target
            val += 0.02 * (d_opp)  # staying a bit farther until you can take space

            # If we can flip, strongly prefer the best flip; else just maximize above.
            if in_opp:
                val += 0.05 * (14 - d_opp)

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]