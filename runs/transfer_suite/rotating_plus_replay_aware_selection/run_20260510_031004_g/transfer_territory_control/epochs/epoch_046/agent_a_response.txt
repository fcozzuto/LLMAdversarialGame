def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target pressure: prefer nearby unclaimed, also consider nudging toward opponent territory boundaries.
    best = (0, 0)
    best_val = -10**18

    opp_dist = max(1, man(sx, sy, px, py))
    toward_opp = 0 if opp_dist < 2 else 1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0

        # Immediate claim value
        if (nx, ny) in unclaimed:
            val += 260
        if (nx, ny) in opp_terr:
            val += 120  # flipping enabled; entering their cell is strong
        if (nx, ny) in self_terr:
            val += 15

        # Encourage expanding outward from our territory (avoid being trapped cycling)
        if (nx, ny) in self_terr:
            val -= 6

        # Voronoi-like: if we get closer to the frontier, do it; if opponent gets closer too, avoid
        d_self = man(nx, ny, px, py)  # distance from our candidate to opponent
        val += int(toward_opp * (40 - 4 * min(d_self, 20)) / 1)

        # Prefer moves that reduce our distance to the nearest unclaimed, otherwise reduce distance to opponent
        if unclaimed:
            near_u = min(unclaimed, key=lambda t: man(nx, ny, t[0], t[1]))
            du = man(nx, ny, near_u[0], near_u[1])
            val += 35 - 3 * min(du, 15)

        # Slightly penalize moving away from our current expansion direction
        if (nx, ny) not in self_terr:
            val += 2

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]