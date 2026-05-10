def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    # Choose resource that we can get first (considering opponent), with deterministic tie-break.
    best_r = resources[0]
    best_val = 10**18
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        md = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        # Prefer resources where we are closer; also break ties toward smaller coordinates.
        val = (md - od) + 0.05 * md + 0.01 * (rx + 7 * ry)
        if val < best_val:
            best_val = val
            best_r = r

    tx, ty = best_r
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Deterministically pick the move that minimizes distance to target while not stepping into obstacles/out of bounds.
    best_m = (0, 0)
    best_d = 10**18
    best_o = 10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist8(nx, ny, tx, ty)
        # Small opponent pressure: prefer moves where opponent is not significantly closer to target next.
        opp_d = dist8(ox, oy, tx, ty)
        # Since opponent position doesn't change here, opp_d is constant; keep tie-break with coordinates.
        if d < best_d or (d == best_d and (nx, ny) < best_m):
            best_d = d
            best_m = (dx, dy)
    return [int(best_m[0]), int(best_m[1])]