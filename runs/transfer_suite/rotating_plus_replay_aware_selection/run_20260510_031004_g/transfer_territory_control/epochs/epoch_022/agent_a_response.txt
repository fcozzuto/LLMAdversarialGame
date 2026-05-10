def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if unclaimed:
        ux, uy = min(unclaimed, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        near_unclaimed = abs(ux - sx) + abs(uy - sy)
    else:
        near_unclaimed = 0

    def adj_opponent(x, y):
        return max(abs(x - px), abs(y - py)) == 1

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 300
        if (nx, ny) in self_terr:
            val += 20
        if (nx, ny) in opp_terr:
            val += 90  # flipping on entry

        # Voronoi-like pull toward nearest unclaimed; also reward reducing distance
        if unclaimed:
            dnew = min(abs(nx - ux) + abs(ny - uy) for ux, uy in unclaimed)
            val += 80 - 5 * dnew

        # Avoid getting surrounded too close to opponent while still allowing flips
        if adj_opponent(nx, ny):
            val -= 35
        # Mild preference to move away if unclaimed exists but opponent is closer
        if unclaimed:
            d_to_opp = abs(nx - px) + abs(ny - py)
            if d_to_opp < near_unclaimed:
                val -= 10

        # Prefer staying within bounds and deterministic tie-breaking
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]