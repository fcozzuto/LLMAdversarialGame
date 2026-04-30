def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def md(a, b, c, d): return abs(a-c) + abs(b-d)
    def step_ok(a, b): return inb(a, b) and (a, b) not in obstacles

    best_res = None
    best_score = None
    for rx, ry in resources:
        d_self = md(x, y, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        # Prefer resources we can reach sooner (or tie) with a bias for being closer.
        s = (d_opp - d_self, -d_self, rx + ry)
        if best_score is None or s > best_score:
            best_score = s
            best_res = (rx, ry)

    def candidate_value(nx, ny):
        if (nx, ny) in obstacles: return -10**9
        if best_res is None:
            # No resources visible: drift toward center, avoid opponent.
            center_x, center_y = (w-1)//2, (h-1)//2
            return -md(nx, ny, center_x, center_y) - 0.05*md(nx, ny, ox, oy)
        rx, ry = best_res
        if (nx, ny) == (rx, ry):
            return 10**7
        d_self = md(nx, ny, rx, ry)
        d_opp_next = md(ox, oy, rx, ry)
        # Encourage shrinking distance to chosen resource and not letting opponent be too close.
        return (d_opp_next - d_self) * 100 - d_self - 0.05*md(nx, ny, ox, oy)

    # If we can take a resource immediately, do it.
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if step_ok(nx, ny) and (nx, ny) in set(tuple(p) for p in resources):
            return [dx, dy]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not step_ok(nx, ny): 
            continue
        v = candidate_value(nx, ny)
        # Small tie-break: prefer moves that increase distance from opponent less aggressively
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]