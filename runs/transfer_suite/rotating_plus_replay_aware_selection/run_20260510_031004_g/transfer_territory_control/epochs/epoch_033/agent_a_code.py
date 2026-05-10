def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    opp_adj = cheb(sx, sy, px, py) == 1

    targets = unclaimed if unclaimed else (opp_terr if opp_terr else set())
    def best_dist(x, y):
        if not targets:
            return 0
        best = None
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 280
        if (nx, ny) in self_terr:
            val += 18
        if (nx, ny) in opp_terr:
            val += 160  # strong pull for flipping on entry

        d_un = best_dist(nx, ny)
        val += -4 * d_un

        # Tactical: prioritize stepping onto opponent cells that are adjacent or advancing
        if (nx, ny) in opp_terr:
            val += 10 * (cheb(nx, ny, px, py) == 1)
            val += 3 * (cheb(nx, ny, px, py) == 0)

        # Defensive: avoid giving opponent a direct adjacency advantage
        # (i.e., don't move closer to opponent if no good capture is available)
        if (nx, ny) not in (unclaimed | self_terr | opp_terr):
            pass
        if val < 120 and cheb(nx, ny, px, py) < cheb(sx, sy, px, py):
            val -= 25

        # Deterministic tie-break: prefer moves with larger immediate val, then smaller dx, then smaller dy
        if val > best_val or (val == best_val and (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]